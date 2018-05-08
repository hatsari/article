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
The latest generation of filesystems also store checksums for the data blocks, in order to fight against silent data corruption. This gives them the ability to detect and correct these random errors, and of course this also comes with a toll in terms of disk usage proportional to the file size.

가장 최신의 파일시스템들은 또한 데이터 블록에 대한 체크섬도 저장한다. 이를 활용해서 silent data corruption(시간이 지남에 따라 데이터가 손실되어 가는 것)을 막을 수 있다. 또한 간헐적으로 발생하는 에러도 찾아내어 고쳐준다. 파일 사이즈에 비례한 디스크 사용 측면에도 영향을 끼친다.

Only more modern systems such as BTRFS and ZFS support data checksums, but some older ones like ext4 have included metadata checksums.

BTRFS나 ZFS와 같은 파일시스템들이 데이터 체크섬을 지원하고, ext4와 같은 오래된 파일스스템은 메타데이터 체크섬만을 지원한다.

### 저널 The journal
ext3 added journaling capabilities to ext2. The journal is a circular log that records transactions in process in order to provide enhanced resiliance against power failures. By default it only applies to metadata, but it can be enabled as well for the data with the  data=journal  option at some performance cost.

*ext3*는 *ext2*에 저널(journal)기능을 추가한 것이다. 저널은 컴퓨터 파워 이슈로 인해 문제가 발생할 때, 이에 대한 데이터 안정성을 보장하기 위해 데이터가 기록될 때의 트랜젝션을 로그로 기록(순환 기록)하는 기능이다. 기본적으로 메타데이터만 기록하나, *data=journal* 옵션을 주면 데이터 트랜잭션 로그도 기록할 수 있다. 단 이 때 성능은 저하된다.

This is a special hidden file, normally at inode number 8 that has a typical size of 128MiB, as the official documentation explains

이 로그는 특별하고 숨겨진 파일이라서 inode 8에 위치하며, 사이즈는 128MiB 이고 공식 문서 이 내용들이 설명되어 있다.

> Introduced in ext3, the ext4 filesystem employs a journal to protect the filesystem against corruption in the case of a system crash. A small continuous region of disk 
> (default 128MiB) is reserved inside the filesystem as a place to land “important” data writes on-disk as quickly as possible. Once the important data transaction is fully written to > the disk and flushed from the disk write cache, a record of the data being committed is also written to the journal. At some later point in time, the journal code writes the t> ransactions to their final locations on disk (this could involve a lot of seeking or a lot of small read-write-erases) before erasing the commit record. Should the system cras> h during the second slow write, the journal can be replayed all the way to the latest commit record, guaranteeing the atomicity of whatever gets written through the journal to> the disk. The effect of this is to guarantee that the filesystem does not become stuck midway through a metadata update.

> *ext3*에서 소개되었던 저널이 *ext4*에도 채용되어 시스템이 망가질 경우 발생할 수 있는 데이터 손상을 방지할 수 있다. 디스크의 연속된 일부 영역이(기본 128MiB) 파일시스템에
> 예약되어 중요한 메타데이터를 가능한 빨리 기록되게 한다. 중요한 데이터 트랜잭션이 완전히 쓰기를 종료하면, 쓰기 캐시를 비우고, 완료된 데이터 로그를 저널에 기록한다. 이 후, 
> 저널 코드는 디스크의 최종 영역에 트랜잭션 로그를 기록한다(이 작업은 많은 찾기 작업과 대량의 작은파일 읽기-쓰기-삭제 작업을 발생시킬 수 있다). 그 다음 완료 로그를 삭제한다.
> 이 후 쓰기 작업 도중 시스템 장애가 발생하면, 저널은 최종 완료(커밋) 기록을 재수행하여 저널을 통해 디스크에 기록된 데이터의 정합성을 보장하게 된다. 이에 따라 메타데이터 에러로 
> 인해 파일시스템이 손상되는 이슈를 방지할 수 있다.

### 테일 패킹 Tail packing
Also known as block suballocation, filesystems with this feature will make use of the tail space at the end of the last block, and share it between different files, effectively packing the tails in a single block.

이는 *block suballocation* 이라고도 불리며, 이 기능이 있는 파일시스템은 마지막 블록의 끝 부분을 사용하고, 다른 파일들과 공유할 수 있어 효율적 디스크 블록을 사용할 수 있다. 

![tail packing](https://ownyourbits.com/wp-content/uploads/2018/05/file_usage4.png)

While this is a nice feature to have that will save us a lot of space specially if we have a big number of small files (as explained above), we can see that it makes existing tools inaccurate to report disk usage. We cannot just add all used blocks of all our files to obtain real disk usage.

위에 설명한 것처럼, 작은 파일이 많은 경우에는 이 기능을 활용하면 많은 데이터 공간을 확보할 수 있기 때문에 매우 효율적이다. 하지만 이 때문에 모니터링툴이 잘못된 디스크 사용 정보를 출력할 수도 있다. 그렇다고 사용중인 모든 블록을 계산해서 실제 디스크 사용량을 보여줄 수도 없다.

Only BTRFS and ReiserFS support this feature.

이 기능은 오직 BTRFS와 ReiserFS만 지원한다.

### 스파스 파일 Sparse files
* 참고: Sparse file: 일반 파일은 파일 내부가 모두 데이터로 채워지나, 스파스 파일은 빈 공간으로 일정 용량의 파일사이즈 공간을 점유할 수 있다. VM 이미지 파일이 대표적이\
다.
----

Most modern filesystems have supported sparse files for a while. Sparse files can have holes in them that are not actually allocated to them and therefore don’t occupy any space. This time, the file size will be bigger than the block usage.

최신 파일시스템들은 스파스 파일을 지원해왔다. 스파스 파일은 파일 안쪽에 빈 공간을 만들 수 있어서 실제 디스크 공간을 차지하고도 파일 사이즈를 점유할 수 있다. 이 때 파일 사이즈는 블록 사용량 보다 크게 된다.

![sparse file](https://ownyourbits.com/wp-content/uploads/2018/04/495px-Sparse_file_en.svg_.png)

This can be really useful for things like generate “big” files really fast, or to provide free space for our VM virtual hard drive on demand. For the first time, weird things can happen such as end up running out of space in the host while we are using our hard drive in the virtual machine.

이 기능은 진짜 *큰* 파일을 빨리 만들 때 유용하다. 또는 VM 가상 디스크에 추가 공간을 제공할 수도 있다. 

In order to slowly create a 10GiB file that uses around 10GiB of disk space we can do

10GiB 파일을 만들 때, 10GiB의 디스크 공간을 채우면서 시간이 오래 걸리는 방법은 아래와 같다.

```shell
$ dd if=/dev/zero of=file bs=2M count=5120$
```

In order to create the same big file instantly we can just write the last byte, or even just

동일한 사이즈의 큰 파일을 바로 생성시키는 방법은 아래와 같다.

```shell
$ dd of=file-sparse bs=2M seek=5120 count=0
```

또는 *truncate* 명령을 사용할 수도 있다.

```shell
$ truncate -s 10G
```

We can modify disk space allocated to a file with the fallocate command that uses the fallocate() system call. With this syscall we can do more advanced things such as

*fallocate()* 시스템콜을 사용하는 *fallocate* 명령어를 사용해서 파일에 할당되어 있는 디스크 공간을 수정할 수도 있다. 이 시스템콜을 이용하여 다음과 같은 고급 작업도 가능하다.

Preallocate space for the file inserting zeroes. This will increase both disk usage and file size.
Deallocate space. This will dig a hole in the file, thus making it sparse and reducing disk usage without affecting file size.
Collapse space, making the file size and usage smaller.
Increase file space, by inserting a hole at the end. This increases file size without affecting disk usage.
Zero holes. This will make the wholes into unwritten extents so that reads will produce zeroes without affecting space or usage.

  - *zero* 로 채워진 파일 미리 할당하기. 파일 사용량과 디스크 사용량 모두 증가.
  - 공간 반환하기. 파일에 빈 공간을 만들어 파일 사이즈는 유지하며 디스크 사용량만 줄이기.
  - 공간 압축. 파일사이즈와 디스크 사용량 모두 줄이기.
  - 파일 끝에 빈 공간을 추가하야 파일 공간 증가. 디스크 사용량은 유지하며 파일 사이즈만 증대.
  - Zero holes. 파일 전체를 쓰여지지 않은 extent 상태로 만들어 파일 공간이나 사용량을 유지하며 *zero*를 추가.
  
For instance, we can dig holes in a file, thus making it sparse in place with

예를 들어, 다음 명령으로 파일에 공간을 만들어 *sparse*로 활용할 수 있다.

```shell
$ fallocate -d file
```

The cp command supports working with sparse files. It tries to detect if the source file is sparse by some simple heuristics and then it makes the destination file sparse as well. We can copy a non-sparse file into a sparse copy with

*cp* 명령은 *sparse* 파일을 지원한다. 즉, 간단한 측정 방법으로 소스 파일이 *sparse* 파일인지를 검사한 후, 맞으면 대상 파일도 *sparse* 파일로 만든다. 또한 *non-sparse* 파일도 *sparse* 파일로 복제할 수 있다.

```shell
$ cp --sparse=always file file_sparse
```

반대로 *sparse* 파일을 *non-sparse* 파일로 복제할 수도 있다.

```shell
$ cp --sparse=never file_sparse file$
```

If you are convinced that you like working with sparse files, you can add this alias to your terminal environment

지금 다루고 있는 파일들이 *sparse* 파일이라고 확신한다면, 터미널 환경에 다음과 같이 *alias* 를 추가할 수도 있다.

```shell
cat ~/.bashrc
alias cp='cp --sparse=always'
```

When processes read bytes in the hole sections the filesystem will provide zeroed pages to them. For instance, we can analyze what happens when the file cache reads from the filesystem in a hole region in ext4. In this case, the sequence in readpage.c looks something like this

프로세스가 빈 공간의 바이트를 읽게 될때, 파일시스템은 *zero* 페이지를 알려준다. 예를 들어, 파일 캐시가 ext4 파일시스템의 빈 공간(hole)을 읽을 때,*readpage.c* 의 순서는 다음과 같다.

```c
(cache read miss) ext4_aops-> ext4_readpages() -> ... -> zero_user_segment()
```	

After this, the memory segment that the process is trying to access through the  read()  system call will efficiently obtain zeroes straight from fast memory.

이 후, *read()* 시스템콜을 통해 접근하려는 프로세스는 효율적으로 메모리에서 *zero* 페이지를 읽어갈 수 있다.

### COW 파일시스템 COW filesystems
The next generation of filesystems after the ext family brings some very interesting features. Probably the most game changing feature from filesystems like ZFS or BTRFS is their COW or copy-on-write abilities.

ext 패미리 다음 세대의 파일시스템들은 몇가지 매우 흥미로운 기능을 지니고 있다. 이 중 ZFS나 BTRFS 같은 파일시스템이 제공하는 가장 흥미로운 기능은 *COW* 또는 *copy-on-write* 기능일 것이다.

When we perform a copy-on-write operation, or a clone, or a reflink or a shallow copy we are really not duplicanting extents. We are just making a metadata annotation in the newly created file, where we reference the same extents from the original file in the new file and we tag the extent as shared. The userspace is now under the illusion that there are two distinct files that can be modified separatedly. Whenever a process wants to write in a shared extent, the kernel will first create a copy of the extent and annotate it as belonging exclusively to that file, at least for now. After this, both files are a bit more different from one another, but they can still share many extents. In other words, in a COW filesystem extents can be shared between files and the filesystem will be in charge of only creating new extents whenever it is necessary.

*copy-on-write* 기능이 수행되거나, 클론(clone)을 하거나, 참조링크(reflink) 또는 *shallo copy* 을 실행하면, 파일 *extent*를 실제로 복제하는 것이 아니다. 이 때는 단순히 새로 생성된 파일의 메타데이터 선언만 만드는 것이다. 즉, 원본 파일의 같은 데이터를 새로운 파일이 참조할 수 있도록 지정하고 해당 데이터가 공유되고 있다는 것을 알리는 태그(tag)를 붙이는 것이다. 하지만 사용자 입장에서는 두 개의 별도의 파일이 각각 별도로 수정될 수 있고 느낄 수 있다. 프로세스가 공유 데이터에 쓰기 작업을 할 때마다, 커널은 먼저 데이터의 복제본을 만들고 그 복제본이 해당 파일에 종속되었음을 알려준다, 적어도 지금까지는 말이다. 이제 두 파일은 서로 약간 달라지게 되었으나 여전히 많은 데이터를 공유하고 있다. 다르게 말하면, COW 파일시스템의 데이터(extent)는 파일간에 공유될 수 있으며, 파일시스템은 필요할 때마다 새로운 데이터만 추가할 수 있게 되었다.

![cow_image](https://ownyourbits.com/wp-content/uploads/2018/05/shared_extent1-768x539.png)

We can see that cloning is a very fast operation, that doesn’t require doubling the space that we use like a regular copy. This is really powerful, and it is the technology behind the instant snapshot abilities of BTRFS and ZFS. You can literally clone ( or take a snapshot ) of you whole root filesystem in under a second. This is useful for instance right before upgrading your packages in case something breaks.

이제 복제(cloning) 작업이 매우 빠르게 수행되는 것을 볼 수 있는데 그 이유는 일반 파일을 복사할 때처럼 해당 공간을 두 배로 소모할 필요가 없기 때문이다. 이 기능은 정말 강력하고, 이 기능을 통해 BTRFS나 ZFS에서 스냅샷을 즉시 만들어내는 방식의 기반 기술이 된다. 그래서 수초만에 root 파일시스템 전체의 복제 또는 스냅샷을 찍을 수 있다. 이를 활용해서 장애 예방으로 시스템 업그레이드 전에 복제를 뜰 수 있다.

BTRFS supports two ways of creating shallow copies. The first one applies to subvolumes and uses the btrfs subvolume snapshot  command. The second one applies to individual files and uses the cp --reflink  command. You can find this alias useful to make fast shallow copies by default.

BTRFS 는 두 가지 방식의 *shallow copy*(참조 복제)를 지원한다. 첫번째는 *subvolumes*를 활용하기 위해 `btrfs subvolume snapshot` 명령을 사용하는 것이다. 두번째는 각각의 파일에 적용하기기 위해 `copy --reflink` 명령을 사용하는 것이다.


```shell
cat ~/.bashrc
cp='cp --reflink=auto --sparse=always'
```

Going one step further, if we have non shallow copies or a file, or even files with duplicated extents, we can deduplicate them to make them reflink those common extents and free up space. One tool that can be used for this is duperemove but beware that this will naturally lead to a higher file fragmentation.

한 단계 더 나아가, *shallow copy* 또는 파일 또는 중복된 데이터(extent)를 가진 파일이 없더라도, 그 파일들을 중복제거할 수 있다. 이 때는 공통의 데이터(extent)를 참조링크(reflink)로 만들고 디스크 공간을 절약할 수 있다. 이 작업을 할 수 있게 해주는 툴이 *deperemove* 이다. 하지만 이 방법은 파일을 더 많이 분할시킬 수 밖에 없다는 것을 명심해야 한다.

Now things really start getting complicated if we are trying to discover how our disk is being used by our files. Tools such as  du  or dutree will just count used blocks without being aware that some of them might be shared so will report more space than what is really being used.

이제 우리 파일이 디스크를 어떻게 점유하게 되는가를 알아내는게 점점 더 복잡해지게 되었다. *du* 또는 *dutree* 같은 명령어는 단순히 사용되는 블록수를 세기만 하고 다른 파일과 공유되는 것은 인식하지 못하여 실제로 더 쓸 수 있는 공간이 있음에도 불구하고 그 공간은 알려주지 못한다.

Similarly, in BTRFS we should avoid using the df  command as it will report space that is allocated by the BTRFS filesystem as free, so it is better to use btrfs filesystem usage.

같은 이유로, BTRFS에서 `df` 명령의 사용을 피해야 한다. 이 명령이 BTRFS 파일시스템이 점유하는 공간을 비어있는 공간으로 잘못 알려줄 것이기 때문이다. 그러므로 파일시스템 사용량을 보기 위해서는 `btrfs filesystem usage` 명령을 사용할 것을 권고한다.

```shell
$ sudo btrfs filesystem usage /media/disk1
Overall:
    Device size:                   2.64TiB
    Device allocated:              1.34TiB
    Device unallocated:            1.29TiB
    Device missing:                  0.00B
    Used:                          1.27TiB
    Free (estimated):              1.36TiB      (min: 731.10GiB)
    Data ratio:                       1.00
    Metadata ratio:                   2.00
    Global reserve:              512.00MiB      (used: 0.00B)
 
Data,single: Size:1.33TiB, Used:1.26TiB
   /dev/sdb2       1.33TiB
 
Metadata,DUP: Size:6.00GiB, Used:3.48GiB
   /dev/sdb2      12.00GiB
 
System,DUP: Size:8.00MiB, Used:192.00KiB
   /dev/sdb2      16.00MiB
 
Unallocated:
   /dev/sdb2       1.29TiB
```

Sadly, I don’t know of any simple way of tracking disk usage of single files in COW filesystems. At the subvolume level we can get a rough idea from tools such as btrfs-du of what amount of data is exclusive to a snapshot and what is shared between snapshots.

불행히도, COW 파일시스템에서 간단하게 각 파일의 디스크 점유량을 추적하는 방법을 알지 못한다. 대신 *subvolume* 레벨에서 `btrfs-du`와 같은 명령어로 독립된 데이터의 용량과 스냅샷 간에 공유되는 용량의 값을 추측할 수 있다.

## 참고 References

https://en.wikipedia.org/wiki/Comparison_of_file_systems

https://lwn.net/Articles/187321/

https://ext4.wiki.kernel.org/index.php/Main_Page


