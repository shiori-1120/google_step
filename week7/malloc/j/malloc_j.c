//
// >>>> malloc challenge! <<<<
//

// >>>> malloc チャレンジ！ <<<<
//

// Your task is to improve utilization and speed of the following malloc
// implementation.
// Initial implementation is the same as the one implemented in simple_malloc.c.
// For the detailed explanation, please refer to simple_malloc.c.

// あなたの課題は、以下の malloc 実装のメモリ利用効率と速度を改善することです。
// 最初の実装は、simple_malloc.c で実装されたものと同じです。
// 詳細な説明については、simple_malloc.c を参照してください。

#include <assert.h>  // assert() 関数のために必要 (デバッグ用のアサート)
#include <stdbool.h> // bool 型 (true/false) のために必要
#include <stddef.h>  // size_t, NULL などのために必要
#include <stdint.h>  // 固定幅整数型 (uint8_t など) のために必要
#include <stdio.h>   // 標準入出力 (printf など) のために必要
#include <stdlib.h>  // 一般ユーティリティ関数 (malloc, free ではないが、他の一般的なもの) のために必要
#include <string.h>  // 文字列操作関数 (memcpy など) のために必要

//
// Interfaces to get memory pages from OS
//

// OSからメモリページを取得するためのインターフェース
//

// システムから指定されたサイズのメモリ領域をマップ（割り当て）する関数
void *mmap_from_system(size_t size);
// システムにマップされたメモリ領域をアンマップ（解放）する関数
void munmap_to_system(void *ptr, size_t size);

//
// Struct definitions
//

// 構造体の定義
//

// 各オブジェクトまたは空きスロットのメタデータ構造体
typedef struct my_metadata_t {
  size_t size;                       // このブロックのサイズ（メタデータ自体は含まない）
  struct my_metadata_t *next;    // 次のフリーリストの要素へのポインタ (空きスロットの場合のみ使用)
} my_metadata_t;

// ヒープ全体の情報を持つ構造体
typedef struct my_heap_t {
  my_metadata_t *free_head; // フリーリストの先頭へのポインタ
  my_metadata_t dummy;      // ダミーノード（フリーリストの操作を簡素化するため）
} my_heap_t;

//
// Static variables (DO NOT ADD ANOTHER STATIC VARIABLES!)
//
// 静的変数（これ以上静的変数を追加しないでください！）
//
my_heap_t my_heap; // グローバルなヒープ情報構造体

//
// Helper functions (feel free to add/remove/edit!)
//

// ヘルパー関数（自由に追加/削除/編集してください！）
//

// フリーリストの先頭に空きスロットを追加する関数
void my_add_to_free_list(my_metadata_t *metadata) {
  assert(!metadata->next); // 追加しようとしているメタデータのnextがNULLであることを確認（デバッグ用）
  metadata->next = my_heap.free_head; // 追加するメタデータのnextを現在のフリーリストの先頭に設定
  my_heap.free_head = metadata;       // フリーリストの先頭を新しく追加したメタデータに更新
}

// フリーリストから空きスロットを削除する関数
void my_remove_from_free_list(my_metadata_t *metadata, my_metadata_t *prev) {
  if (prev) { // 削除するスロットの前のスロット（prev）が存在する場合
    prev->next = metadata->next; // prevのnextを、削除するスロットのnextに繋ぎ変える
  } else {    // 削除するスロットがフリーリストの先頭だった場合
    my_heap.free_head = metadata->next; // フリーリストの先頭を、削除するスロットのnextに更新
  }
  metadata->next = NULL; // 削除されたスロットのnextをNULLに設定（安全のため）
}

//
// Interfaces of malloc (DO NOT RENAME FOLLOWING FUNCTIONS!)
//

// malloc のインターフェース（以下の関数の名前を変更しないでください！）
//

// 各チャレンジの最初に呼び出されます。
void my_initialize() {
  my_heap.free_head = &my_heap.dummy; // フリーリストの先頭をダミーノードに設定
  my_heap.dummy.size = 0;                 // ダミーノードのサイズは0
  my_heap.dummy.next = NULL;              // ダミーノードのnextはNULL
}

// my_malloc() はオブジェクトが割り当てられるたびに呼び出されます。
// |size| は8バイトの倍数であり、8 <= |size| <= 4000 の範囲であることが保証されます。
// mmap_from_system() / munmap_to_system() 以外のライブラリ関数は使用できません。
void *my_malloc(size_t size) {
  my_metadata_t *metadata = my_heap.free_head; // フリーリストの先頭から探索を開始
  my_metadata_t *prev = NULL;                      // 現在のメタデータの前のメタデータを保持するポインタ
  // First-fit（初回適合）: オブジェクトが収まる最初の空きスロットを見つけます。
  // TODO: このロジックを Best-fit（最適適合）に更新してください！
  while (metadata && metadata->size < size) { // メタデータが存在し、かつそのサイズが要求されたサイズより小さい間繰り返す
    prev = metadata;                          // 現在のメタデータをprevに保存
    metadata = metadata->next;                // 次のフリーリストの要素へ移動
  }
  // この時点で、metadata は最初に見つかった空きスロットを指し、
  // prev はその前のエントリです。

  if (!metadata) { // 適切なサイズの空きスロットが見つからなかった場合
    // 利用可能な空きスロットがありませんでした。
    // mmap_from_system() を呼び出して、システムから新しいメモリ領域を要求する必要があります。
    //
    //     | metadata | free slot |
    //     ^
    //     metadata
    //     <---------------------->
    //           buffer_size
    //
    size_t buffer_size = 4096; // 新しく要求するメモリ領域のサイズ（4KB）
    my_metadata_t *metadata = (my_metadata_t *)mmap_from_system(buffer_size); // システムからメモリを割り当て、その先頭をメタデータとして扱う
    metadata->size = buffer_size - sizeof(my_metadata_t); // 新しいスロットのサイズを設定（メタデータのサイズ分を引く）
    metadata->next = NULL; // 新しいスロットのnextをNULLに設定
    // このメモリ領域をフリーリストに追加します。
    my_add_to_free_list(metadata);
    // これで、my_malloc() を再度試行します。これは成功するはずです。
    return my_malloc(size);
  }

  // |ptr| は割り当てられたオブジェクトの開始位置です。
  //
  // ... | metadata | object | ...
  //     ^          ^
  //     metadata   ptr
  void *ptr = metadata + 1; // メタデータの直後がオブジェクトの開始位置
  size_t remaining_size = metadata->size - size; // 空きスロットの残りのサイズを計算
  // フリーリストから空きスロットを削除します。
  my_remove_from_free_list(metadata, prev);

  if (remaining_size > sizeof(my_metadata_t)) {
    // 割り当てられたオブジェクトのメタデータを縮小し、
    // remaining_size に対応する残りの領域を分離します。
    // もし remaining_size が新しいメタデータを作成するのに十分な大きさでなければ、
    // このコードパスは実行されず、その領域は割り当てられたオブジェクトの一部として管理されます。
    metadata->size = size; // 割り当てられたオブジェクトのメタデータのサイズを、要求されたサイズに更新
    // 残りの空きスロットのために新しいメタデータを作成します。
    //
    // ... | metadata | object | metadata | free slot | ...
    //     ^          ^        ^
    //     metadata   ptr      new_metadata
    //                <------><---------------------->
    //                  size      remaining size
    my_metadata_t *new_metadata = (my_metadata_t *)((char *)ptr + size); // 割り当てたオブジェクトの直後が新しいメタデータの開始位置
    new_metadata->size = remaining_size - sizeof(my_metadata_t); // 新しいフリースロットのサイズを設定
    new_metadata->next = NULL; // 新しいフリースロットのnextをNULLに設定
    // 残りの空きスロットをフリーリストに追加します。
    my_add_to_free_list(new_metadata);
  }
  return ptr; // 割り当てられたオブジェクトの開始位置を返す
}

// オブジェクトが解放されるたびに呼び出されます。
// mmap_from_system / munmap_to_system 以外のライブラリ関数は使用できません。
void my_free(void *ptr) {
  // メタデータを探します。メタデータはオブジェクトの直前に配置されています。
  //
  // ... | metadata | object | ...
  //     ^          ^
  //     metadata   ptr
  my_metadata_t *metadata = (my_metadata_t *)ptr - 1; // オブジェクトの開始位置から1つ前（メタデータ分）に戻ってメタデータを取得
  // フリーリストに空きスロットを追加します。
  my_add_to_free_list(metadata);
}

// 各チャレンジの最後に呼び出されます。
void my_finalize() {
  // 現時点では何もありません。
  // 必要であれば、何か追加しても構いません！
}

void test() {
  // ここに実装してください！
  assert(1 == 1); /* 1 は 1 です。これは常に真です！（削除しても構いません。）*/
}