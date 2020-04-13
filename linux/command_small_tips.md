# Mac Small Tips
## Homebrew
installation
1. xcode-select --install
2. /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

## emacs
- installation
    brew cask install emacs
- meta
    on terminal app -> perferance -> profiles -> check [use Option as Meta key]
- read only mode
    C-x C-q
    or
    M-x read-only-mode (toggle)
- print hardcopy in nice shape
    M-x ps-print-buffer-with-faces
- auto parentheses
    M-x electric-pair-mode
    M-x show-paren-mode
- remove blank space
    M-\
- indent to next line
    C-j
- mark and move to mark point
    C-@: mark, C-x C-x: move to mark point
- python
    C-c C-p : create python shell
    C-c C-c : run code

### copy region to clipboard
- on mac
  [option]+| pbcopy RET


## aws
- run again - cloudinit userdata
    rm /var/lib/cloud/instance/scripts/userdata.txt
    rm /var/lib/cloud/instances/*/sem/config_scripts_user
### On S3, list objects over 1,000
  ec2-user@dev aws s3api list-objects --bucket *bucket_name*

## mac
- safari - mouse not working
    rm -i ~/Library/Caches/com.apple.Safari/Cache.db*
