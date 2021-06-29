" -----------------
" |   BOOTSTRAP   |
" -----------------

" first line, because it changes other options as side effect
" most known setting as it allows usage of cursor keys
set nocompatible

" ---------------
" |   GENERAL   |
" ---------------

" move backup/swap files to tmp
set backupdir=/tmp
set dir=/tmp

" colors
" set t_ut=                         " disable Background Color Erase (BCE)
                                    " by clearing the t_ut terminal option
                                    " (forces background repainting; only
                                    " required if VIM background differs
                                    " from TERM background; slow process)
set t_Co=256                        " enable to 256 colors

" color scheme
set background=light                " default light
" set background=dark               " default dark
" ---------------------------------
" colorscheme jellybeans            " best in diff
" ---------------------------------
" colorscheme Tomorrow-Night        " best in dark
" colorscheme Tomorrow              " best in light

" color modification for diff mode
" bash color names see: http://misc.flogisoft.com/_media/bash/colors_format/256-colors.sh.png
highlight DiffAdd    cterm=none ctermfg='Black' ctermbg='Green'   gui=none guifg='Black' guibg='Green'
highlight DiffDelete cterm=none ctermfg='Black' ctermbg='Red'     gui=none guifg='Black' guibg='Red'
highlight DiffChange cterm=none ctermfg='Black' ctermbg='Cyan'    gui=none guifg='Black' guibg='Cyan'
highlight DiffText   cterm=none ctermfg='Black' ctermbg='Yellow' gui=none guifg='Black' guibg='Magenta'

" react on escape key instantaneous (otherwise vi waits a grace period for possible escape sequence
" and doesn't leave insert mode fast enough for my liking)
set timeoutlen=1000 ttimeoutlen=0

" disable all kind of bells (freezes UI, e.g. when you scroll out of bounds)
set noerrorbells visualbell t_vb=

" disable auto indenting
setlocal noautoindent
setlocal nocindent
setlocal nosmartindent
setlocal indentexpr=
" alternatively, disable on key: nnoremap <F?> :setl noai nocin nosi inde=<CR>

" tabs to spaces
setlocal smarttab
setlocal expandtab
setlocal shiftwidth=2
setlocal tabstop=2
setlocal softtabstop=2

" switch tabs
nnoremap <TAB> gt
nnoremap <S-TAB> gT
" less convenient,   : nnoremap <C-n> gt
" but leaves tab free: nnoremap <C-p> gT

" split windows
nnoremap <C-W>h <C-W>s
inoremap <C-W>h <ESC><C-W>si

" save (make sure to have run stty -ixon before to avoid terminal scroll-lock)
nnoremap <C-S> :w!<CR>
inoremap <C-S> <ESC>:w!<CR>

" quit
nnoremap <C-C> :q<CR>                       " quit single
nnoremap <C-D> :qa<CR>                      " quit all
nnoremap <C-Q> :bp<bar>sp<bar>bn<bar>bd<CR> " quit buffer without quiting window
inoremap <C-C> <ESC>:q<CR>
inoremap <C-D> <ESC>:qa<CR>
inoremap <C-Q> <ESC>:bp<bar>sp<bar>bn<bar>bd<CR>

" sudo save if you forgot to open the file with sudo privileges
cnoremap w!! w !sudo tee % >/dev/null

" do no longer jump down/up over wrapped lines
nnoremap j gj
nnoremap k gk
nnoremap <Down> gj
nnoremap <Up> gk

" reload
nnoremap <F5> :edit<CR>

" give VIM more memory
set history=1000
set undolevels=1000

" let VIM ignore stuff we don't care about
set wildignore=*.swp,*.bak,*.pyc,*.class

" show matching parenthesis
set showmatch

" mouse mode (disabled here to not conflict with native OS mouse support)
" set mouse=a
" set ttymouse=xterm2
" set ttyfast
" disable visual mode/selection
noremap <LeftDrag> <LeftMouse>
noremap! <LeftDrag> <LeftMouse>
" disable extend visual block
noremap <RightMouse> <nop>
noremap! <RightMouse> <nop>

" search
set ignorecase
set incsearch
set hlsearch
nnoremap <silent> <Space> :nohlsearch<Bar>:echo<CR>

" run searches in "very magic" mode, i.e. extended regex compliant
nnoremap ? ?\v
vnoremap ? ?\v
nnoremap / /\v
vnoremap / /\v
cnoremap %s/ %smagic/
cnoremap \>s/ \>smagic/
nnoremap :g/ :g/\v
nnoremap :g// :g//