# Understanding disk usage in Linux
original: https://ownyourbits.com/2018/05/02/understanding-disk-usage-in-linux/

이 문서는 파일이 디스크에 저장될 때 실제로 얼마만큼의 디스크 공간을 차지하게 되는지 알아보는 내요입니다. 단순히 파일사이즈 만큼 저장되는 것이 아니라 block 사이즈에 따른 변화, journal 또는 extent, sparse 공간에 따른 저장용량의 변화를 확인하실 수 있습니다. 기존 ext 파일시스템부터 최신 btrfs, xfs 까지도 다루므로 파일시스템에 따른 특징도 알아볼 수 있습니다.

---

![dutree screenshot](https://ownyourbits.com/wp-content/uploads/2018/03/dutree-featured2.png)

How much space is this file taking from my hard drive? How much free space do I have? How many more files can I fit in the remaining free space?
이 파일이 내 하드드라이브에서 얼마나 공간을 차지할까? 빈 공간이 얼마나 남은거지? 나머지 빈 공간에 파일을 얼마나 더 저장할 수 있을까?

The answer to these questions seems obvious. We all have an instinctive understanding of how filesystems work, and we often picture storing files in disk space in the same way as physically fitting apples inside a basket.
이런 질문에 대한 대답은 어찌보면 명확해 보인다. 우리는 파일시스템이 어떻게 동작하는지도 직감으로 알고 있고, 바구니에 사과를 넣는 것처럼 디스크 공간에 파일을 넣는 것으로 생각하곤 한다. 

In modern Linux systems though, this intuition can be misleading. Let us see why.
하지만 최신 리눅스 시스템에서 이런 직감은 틀린 것이다. 그럼 그 이유를 알아보자.

## 파일 사이즈 File size
What is the size of a file? This one seems easy: the summation of all bytes of content from the beginning of the file until the end of the file.
파일 사이즈는 무엇일까? 이건 좀 쉬워 보인다: 파일의 시작부터 끝까지 채워지는 바이트의 합.

We often picture all file contents layed out one byte after another until the end of the file.
보통 파일 용량은 한바이트씩 파일의 끝까지 채워가는 것으로 생각할 수 있다.

![sum of bytes](https://ownyourbits.com/wp-content/uploads/2018/05/file_usage1.png)

And that’s how we commonly think about file size. We can get it with
그리고 이 그림이 우리가 보통 생각하는 파일 사이즈의 모습이다. 다음 명령으로 그 값을 알 수 있다.

```shell
ls -l file.c
```

, or the stat command that makes use of the stat() system call.
, 또는 *stat()* 시스템콜을 사용하는  *stat* 명령으로도 알 수 있다. 

```shell
stat file.cs
```

Inside the Linux kernel, the memory structure that represents the file is the inode. The metadata that we can access through the  stat  command lives in the inode
리눅스 커널 내부에서, 파일을 표현하는 메모리 구조는 *inode*이다. *stat*명령을 통해 접근할 수 있는 메타데이터는 *inode*에 저장되어 있다.

```c
include/linux/fs.h

struct inode {
    /* excluded content */

    loff_t              i_size;       /* file size */
    struct timespec     i_atime;      /* access time */
    struct timespec     i_mtime;      /* modification time */
    struct timespec     i_ctime;      /* change time */
    unsigned short      i_bytes;      /* bytes used (for quota) */
    unsigned int        i_blkbits;    /* block size = 1 << i_blkbits */
    blkcnt_t            i_blocks;     /* number of blocks used */

   /* excluded content */
}
```

We can see some familiar attributes, such as the access and modification timestamps, and also we can see  *i_size*, which is the file size as we defined earlier.
여기서 몇가지 익숙한 어트리뷰트를 볼 수 있는데, access 와 modification 시간 그리고 *i_size*(글 초반에 정의했던 파일 사이즈)와 같은 것들이다.

Thinking in terms of the file size is intuitive, but we are more interested in how space is actually used.
파일 사이즈를 직관적으로 생각해보았지만, 여전히 실제 디스크 공간이 어떻게 사용되는가를 더 알아보도록 하겠다.

## 블록과 블록 사이즈 Blocks and block size

Regarding how the file is stored internally, the filesystem divides storage in blocks. Traditionally the block size was 512 bytes, and more recently 4 kilobytes. This value is chosen based on supported page size for typical MMU hardware.

파일이 내부적으로 어떻게 저장되는가에 대해 생각해보면, 파일시스템은 스토리지를 블록(block)으로 구분한다. 전통적으로 블록 사이즈는 512 바이트였다. 하지만 최근에는 4 키로바이트로 바뀌었으며, 이 값은 MMU 하드웨어에서 지원하는 페이지 사이즈(page size)를 기반으로 결정된다.

The filesystem inserts our chunked file into those blocks, and keeps track of them in the metadata.
파일시스템은 이 블록들 안에 파일 조각(chunk)을 집어 넣는다. 그리고 메타데이터로 각 조각들이 어디에 저장되는가를 기록한다.

This ideally looks like this
그래서 이상적으로는 아래와 같은 그림이 나온다.

![ideal file chunks in blocks](https://ownyourbits.com/wp-content/uploads/2018/05/file_usage2.png)

, but in practice files are constantly created, resized and destroyed, and it looks more like this
, 그러나 실제 환경에서는 파일이 지속적으로 생성되고, 사이즈가 변경되고 삭제되기 때문에 실제 그림으로 나타내면 다음과 같다.

![practical file chunks in blocks](https://ownyourbits.com/wp-content/uploads/2018/05/file_usage3.png)

This is known as external fragmentation, and traditionally results in a performance degradation due to the fact that the spinning head of the hard drive has to jump around gathering the fragments and that is a slow operation. Classic defragmentation tools try to keep this problem at bay.

이런 모습은 외부 파편화(external fragmentation)으로 불리우며, 이 때문에 성능 저하가 발생한다. 그 이유는 파편화된 파일 조각을 모으기 위해 하드 드라이브의 스핀 헤드가 이곳 저곳 돌아다녀야 하기 때문이다. 그래서 일반적인 디스크 조각 모음 도구들이 이런 문제를 해결하는데 사용됩니다.

What happens with files smaller than 4kiB? what happens with the contents of the last block after we have cut our file into pieces? Naturally there is going to be wasted space there, we call that phenomenon internal fragmentation. Obviously this is an undesirable side effect that can make unusable a lot of free space, much more so when we have a big number of very small files.

그럼 4kiB 보다 작은 파일이 저장될 때는 어떤 일이 발생할 것인가? 또 파일을 조각으로 분리할 때 마지막 파일 블록은 어떻게 처리될 것인가? 보통은 나머지 공간들은 버려지게 된다. 그리고 그 현상을 내부 파편화(internal fragmentation) 이라고 부른다. 확실히 이렇게 많은 여유 공간을 사용하지 못하고 남겨구는 것은 비효율적이며, 특히나 매우 작은 파일이 많이 있을 경우에는 이런 문제가 더 큰게 다가온다.

We can see the real disk usage of the file with stat, or

*stat* 명령으로 파일의 실제 *디스크 사용량(disk usage)* 을 보고나 또는

```shell
ls -ls file.c
```

또는 *du* 명령으로도 알 수 있다.

```shell
du file.c
```

For example, the contents of this one byte file still use 4kiB of disk space.
예를 들어, 1 바이트 파일은 4kiB의 디스크 공간을 소비한다.

```shell
$ echo "" > file.c
 
$ ls -l file.c
-rw-r--r-- 1 nacho nacho 1 Apr 30 20:42 file.c
 
$ ls -ls file.c
4 -rw-r--r-- 1 nacho nacho 1 Apr 30 20:42 file.c
 
$ du file.c
4 file.c
 
$ dutree file.c
[ file.c 1 B ]
 
$ dutree -u file.c
[ file.c 4.00 KiB ]
 
$ stat file.c
 File: file.c
 Size: 1 Blocks: 8 IO Block: 4096 regular file
Device: 2fh/47d Inode: 2185244 Links: 1
Access: (0644/-rw-r--r--) Uid: ( 1000/ nacho) Gid: ( 1000/ nacho)
Access: 2018-04-30 20:41:58.002124411 +0200
Modify: 2018-04-30 20:42:24.835458383 +0200
Change: 2018-04-30 20:42:24.835458383 +0200
 Birth: -
```

We are therefore looking at two magnitudes, file size and blocks used. We tend to think in terms of the former, but we should think in terms of the latter.
여기서 우리는 두가지 부분을 확인해 보았다. 사용된 파일 사이즈와 블록 사이즈. 보통 우리는 전자(사용된 파일 사이즈)를 고려하는 경향이 있지만, 실제로는 후자(사용된 블록사이즈)를 염두에 두어야 한다.

## 파일시스템별 특징 Filesystem specific features

In addition to the actual contents of the file, the kernel needs to store all sorts of metadata. We have seen some of the metadata in the inode already, and there also is other that is familiar to any Unix user, such as mode, ownership, uid, gid , flags, and ACL.

파일의 실제 내용과 더불어, 커널은 모든 종류의 메타데이터도 저장해야 한다. 앞서서 *inode*에 메타데이터 중 일부가 저장되는 것을 확인하였다. 하지만 유닉스 사용자에게 익숙한 mode, ownership, uid, gid, 플래그 그리고 ACL(access control list)와 같은 요소들도 많이 있다.

```c
struct file {
    /* excluded content */
 
    struct fown_struct    f_owner;
    umode_t i_mode;
    unsigned short i_opflags;
    kuid_t i_uid;
    kgid_t i_gid; 
    unsigned int i_flags;
 
    /* excluded content */
}
```

There are also other structures such as the superblock that represents the filesystem itself, vfsmount that represents the mountpoint, redundancy information, namespaces and more. Some of this metadata can also take up some significant space, as we’ll see.

또한 파일시스템 자체에 대한 정보와 마운트포인트를 나타내는 vfsmount, 리던던시 정보(redundancy information), 네임스페이스 등을 담고 있는 슈퍼블록(superblock)과 같은 다른 구조체도 존재한다. 이런 메타데이터 정보의 일부는 굉장히 많은 공간을 차지할 수 있는데 이 부분은 아래에서 살펴보도록 하겠다.

### 블록 할당 메타데이터 Block allocation metadata
This one will highly depend on the filesystem that we are using, as they will keep track of which blocks correspond to a file in their own unique way. The traditional ext2 way of doing this is through the i_block table of direct and indirect blocks.

블록 할당 메타데이터는 우리가 사용중인 파일시스템에 매우 의존적이다. 이 메타데이터는 파일시스템 특성에 따라 파일에 대응되는 블록을 계속 기록해 나간다. 전통적인 *ext2* 방식은 direct와 indirect 블록의 *i_block* 테이블을 사용한다.

![i_block table of ext2](https://ownyourbits.com/wp-content/uploads/2018/04/Ext2-inode.gif)

그리고 아래는 이에 해당하는 메모리 구조체이다.

fs/ext2/ext2.h
```c
/*
 * Structure of an inode on the disk
 */
struct ext2_inode {
    __le16  i_mode;     /* File mode */
    __le16  i_uid;      /* Low 16 bits of Owner Uid */
    __le32  i_size;     /* Size in bytes */
    __le32  i_atime;    /* Access time */
    __le32  i_ctime;    /* Creation time */
    __le32  i_mtime;    /* Modification time */
    __le32  i_dtime;    /* Deletion Time */
    __le16  i_gid;      /* Low 16 bits of Group Id */
    __le16  i_links_count;  /* Links count */
    __le32  i_blocks;   /* Blocks count */
    __le32  i_flags;    /* File flags */
 
   /* excluded content */
 
    __le32  i_block[EXT2_N_BLOCKS];/* Pointers to blocks */
 
   /* excluded content */
 
}
```

As files get bigger, this scheme can produce a huge overhead because we have to track thousands of blocks for a single file. Also, we have a size limitation, as the 32bit ext3 filesystem can handle to only 8TiB files using this mechanism. ext3 developers have been keeping up with the times by supporting 48 bytes, and by introducing extents.
파일들이 커짐에 따라, 이 스키마는 큰 오버헤드를 만들 수 있다. 왜냐하면 하나의 파일때문에 수천개의 블록의 트래킹해야하기 때문이다. 또한 크기 제한도 있어서 이 방식으로는 32bit ext3 파일시스템에서 오직 8TiB 파일만 다룰 수 있다. 그래서 *ext3* 개발자들은 48 bytes를 지원하도록 노력해왔고 또한 *extent*도 개발하게 되었다.

```c
struct ext3_extent {
    __le32    ee_block;    /* first logical block extent covers */
    __le16    ee_len;        /* number of blocks covered by extent */
    __le16    ee_start_hi;    /* high 16 bits of physical block */
   __le32    ee_start;    /* low 32 bits of physical block */
};
``` 

The concept is really simple: allocate contiguous blocks in disk and just anotate where the extent starts and how big it is. This way, we can allocate big groups of blocks to a file using way less metadata, and also benefit from faster sequencial access and locality.
*extent* 개념은 정말로 간단하다. 연속되는 블록을 디스크에 할당하고, *extent*가 시작하는 시점과 사이즈가 얼마나 큰지만 알려주면 된다. 이런 방식에서 큰 그룹의 블록을 훨씬 적은 메타데이터로 할당할 수 있게 되었으며, 훨씬 빨리 연속된 데이터를 접근할 수 있게 되었다.

For the curious, ext4 is backwards compatible, so it supports both methods: indirect method and extents method. To see how space is allocated, we can look at a write operation. Writes don’t go straight to storage, but first they land in the file cache for performance reasons. At some point, the cache writes back the information to persistent storage.

흥미롭게도, *ext4*는 ext3와 호환성을 가지면서 두 가지 방식을 모두 지원한다: *indirect* 방식과 *extent* 방식. 디스크 공간이 어떻게 할당되는가를 알아보기 위해, *쓰기 방식(write operation)*을 알아 보겠다. *쓰기(write)*는 디스크 스토리지에 바로 쓰여지지 않는다. 성능을 높이기 위해 파일 캐시에 먼저 저장되고, 특정 시점에 캐시가 스토리지에 기록되는 방식이다.

The filesystem cache is represented by the struct address_space, and the writepages operation will be called on it. The sequence looks like this
파일시스템 캐시는 *address_space* 구조체로 표현되고, *writepages* 기능이 이를 호출한다. 그 순서는 다음과 같다.

```c
(cache writeback) ext4_aops-> ext4_writepages() -> ... -> ext4_map_blocks()
```

, at which point, ext4_map_blocks()  will call either ext4_ext_map_blocks() , or  ext4_ind_map_blocks()  depending on wether we are using extents or not. If we look at the former in extents.c, we’ll notice references to the notion of holes that we will cover in the next section.

그리고 어느 순간에 *ext4_map_blocks()* 가 ext4_ext_map_blocks() 또는 ext4_ind_map_blocks()를 호출할 것이다. 이는 *extent*를 사용하냐 또는 사용하지 않느냐에 따라 달라진다. *extents.c*의 앞부분을 보면, 다음 장에서 다룰 *구멍(holes)* 개념이 참조됨을 알아차릴 수 있을 것이다.

### 체크섬 Checksums
