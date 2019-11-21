" -----------------
" |   BOOTSTRAP   |
" -----------------

" first line, because it changes other options as side effect
" most known setting as it allows usage of cursor keys
set nocompatible

" set runtime path dynamically based on user env home
set runtimepath+=$DOTFILES_HOME/.vim

" ------------
" |   HELP   |
" ------------
"
" Special Keys             Description
" ------------             -----------
" <BS>                     Backspace
" <Tab>                    Tab
" <CR>                     Enter
" <Enter>                  Enter
" <Return>                 Enter
" <Esc>                    Escape
" <Space>                  Space
" <Up>                     Up arrow
" <Down>                   Down arrow
" <Left>                   Left arrow
" <Right>                  Right arrow
" <F1> - <F12>             Function keys 1 to 12
" #1, #2..#9,#0            Function keys F1 to F9, F10
" <Insert>                 Insert
" <Del>                    Delete
" <Home>                   Home
" <End>                    End
" <PageUp>                 Page-Up
" <PageDown>               Page-Down
" <bar>                    the '|' character, which otherwise needs to be escaped '\|'
"
" Commands                 Mode
" --------                 ----
" nmap, nnoremap, nunmap   Normal mode
" imap, inoremap, iunmap   Insert and Replace mode
" vmap, vnoremap, vunmap   Visual and Select mode
" xmap, xnoremap, xunmap   Visual mode
" smap, snoremap, sunmap   Select mode
" cmap, cnoremap, cunmap   Command-line mode
" omap, onoremap, ounmap   Operator pending mode
"
" 'nore' stands for 'no'n-'recursive', i.e. such mappings are executed directly and
" not resolved recursively. It's generally good practice to do all mappings with it.
"   Example: x will 1 line and c will delete 2 characters, NOT 2 lines:
"   nnoremap x dd
"   nnoremap c xx
" 'un' unmaps existing mappings.
"
" In terminals certain key mappings like shift + function key don't work or are mapped
" differently from terminal to terminal. In such cases, define multiple mappings for your
" more important terminals. To get the proper escape sequences run 'cat' and press the
" key combinations you need (replace the first ^[ which is the escape key with <C-[>).

" ---------------
" |   GENERAL   |
" ---------------

" move backup/swap files to tmp
set backupdir=/tmp
set dir=/tmp

" fix shift + function keys; see http://unix.stackexchange.com/questions/58361/how-to-fix-the-shifted-function-keys-in-vim-in-xterm-in-gnome-terminal
function! FixShiftFunctionKeys()
  let a=0
  let b='PQRS'
  while a < 4
    exec 'set <s-f' . (a + 1) . ">=\eO1;2" . b[a]
    let a+=1
  endwhile
  let a=5
  let b='1517181920212324'
  let c=0
  while a < 16
    exec 'set <s-f' . a . ">=\e[" . b[c : c + 1] . ';2~'
    let a+=1
    let c+=2
  endwhile
endfunction
call FixShiftFunctionKeys()

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

" color scheme for airline
let g:airline_theme = 'airlineish'

" color modification for diff mode
" bash color names see: http://misc.flogisoft.com/_media/bash/colors_format/256-colors.sh.png
highlight DiffAdd    cterm=none ctermfg='Black' ctermbg='Green'   gui=none guifg='Black' guibg='Green'
highlight DiffDelete cterm=none ctermfg='Black' ctermbg='Red'     gui=none guifg='Black' guibg='Red'
highlight DiffChange cterm=none ctermfg='Black' ctermbg='Cyan'    gui=none guifg='Black' guibg='Cyan'
highlight DiffText   cterm=none ctermfg='Black' ctermbg='Yellow' gui=none guifg='Black' guibg='Magenta'

" syntax highlighting
syntax on

" register more than the default events for checktime (useful in combination with :autoread)
au FocusGained,BufEnter,BufWinEnter,CursorHold,CursorMoved * :checktime

" react on escape key instantaneous (otherwise vi waits a grace period for possible escape sequence
" and doesn't leave insert mode fast enough for my liking)
set timeoutlen=1000 ttimeoutlen=0

" disable all kind of bells (freezes UI, e.g. when you scroll out of bounds)
set noerrorbells visualbell t_vb=

" disable auto-commenting (on next line if previous was a comment)
autocmd FileType * setlocal formatoptions-=c formatoptions-=r formatoptions-=o

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

" moving around
" let save_cursor = getpos(".")
" call setpos('.', save_cursor)
nnoremap <C-PageUp> gg
nnoremap <C-[>[5;5~ gg
nnoremap <C-PageDown> G
nnoremap <C-[>[6;5~ G
" scroll up/down line-wise; see http://vim.wikia.com/wiki/VimTip105
function! s:SavingScroll(cmd)
  let save_scroll = &scroll
  execute 'normal! ' . a:cmd
  let &scroll = save_scroll
endfunction
nnoremap <S-Up> :call <SID>SavingScroll("1<C-V><C-U>")<CR>
inoremap <S-Up> <Esc>:call <SID>SavingScroll("1<C-V><C-U>")<CR>i
vnoremap <S-Up> <Esc>:call <SID>SavingScroll("gv1<C-V><C-U>")<CR>
nnoremap <S-Down> :call <SID>SavingScroll("1<C-V><C-D>")<CR>
inoremap <S-Down> <Esc>:call <SID>SavingScroll("1<C-V><C-D>")<CR>i
vnoremap <S-Down> <Esc>:call <SID>SavingScroll("gv1<C-V><C-D>")<CR>
" scroll up/down page-wise; see http://vim.wikia.com/wiki/Page_up/down_and_keep_cursor_position
function! ComputeWindowHeigth()
  " open all folds to get the right line numbers, but it would be better
  " to get the window heigth independent of the line numbers
  if !&diff " unfortunately we can't open folds in diff mode on one side only
    silent! %foldopen!
  endif
  let top_line = line("w0")
  let bottom_line = line("w$")
  let visible_lines = bottom_line - top_line + 1
  return visible_lines
endfunction
function! s:SavingScrollN(cmd)
  let save_scroll = &scroll
  let scroll_lines = ComputeWindowHeigth() - 1
  execute 'normal! ' . scroll_lines . a:cmd
  let &scroll = save_scroll
endfunction
nnoremap <PageUp> :call <SID>SavingScrollN("<C-V><C-U>")<CR>
nnoremap <PageDown> :call <SID>SavingScrollN("<C-V><C-D>")<CR>
" ... option B
" nnoremap <silent> <PageUp> :set scroll=0<CR>:set scroll^=2<CR>:set scroll-=1<CR><C-U>:set scroll=0<CR>
" nnoremap <silent> <PageDown> :set scroll=0<CR>:set scroll^=2<CR>:set scroll-=1<CR><C-D>:set scroll=0<CR>
" ... option C
" nnoremap <silent> <PageUp> <C-U><C-U>
" vnoremap <silent> <PageUp> <C-U><C-U>
" inoremap <silent> <PageUp> <C-\><C-O><C-U><C-\><C-O><C-U>
" nnoremap <silent> <PageDown> <C-D><C-D>
" vnoremap <silent> <PageDown> <C-D><C-D>
" inoremap <silent> <PageDown> <C-\><C-O><C-D><C-\><C-O><C-D>

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

" auto reload
function! AutoReload()
" set autoread works only on the events registered for checktime, so let's use Python
" background threads to overcome this and update a buffer independent of user interaction
echo "Launching auto reload background thread. Press CTRL-C to exit VIM."
python << EOF
import time, vim
try: import thread
except ImportError: import _thread as thread # Py3

def autoread():
    vim.command('checktime')  # Run the 'checktime' command
    vim.command('redraw')     # Actually update the display

def autoread_loop():
    while True:
        time.sleep(1)
        autoread()

thread.start_new_thread(autoread_loop, ())
EOF
endfunction
nnoremap <silent> <S-F5> :call b:AutoReload()<CR>

" edit/source vimrc file
nnoremap <silent> <leader>ev :e $DOTFILES_HOME/.vimrc<CR>
nnoremap <silent> <leader>sv :so $DOTFILES_HOME/.vimrc<CR>

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

" toggle diff mode for a buffer
function! DiffModeToggle()
  if &diff
    diffoff!
" example of how to also switch the colorscheme:
"   set background=light
"   colorscheme Tomorrow
    nnoremap <F5> :edit<CR>
    syntax on
    SyntasticCheck
  else
    diffthis
" example of how to also switch the colorscheme:
"   set background=dark
"   colorscheme jellybeans
    nnoremap <F5> :diffupdate<CR>
    syntax off
    SyntasticToggleMode
  endif
endfunction
nnoremap <F6> :call DiffModeToggle()<CR>
" au FilterWritePost * if &diff | set background=dark | colorscheme jellybeans | nnoremap <F5> :diffupdate<CR> | syntax off | SyntasticToggleMode | else | set background=light | colorscheme Tomorrow | nnoremap <F5> :edit<CR> | syntax on | SyntasticCheck | endif
au FilterWritePost * if &diff | nnoremap <F5> :diffupdate<CR> | ":SyntasticToggleMode" | else | nnoremap <F5> :edit<CR> | syntax on | SyntasticCheck | endif
" au BufWinLeave * diffoff! | set background=light | colorscheme Tomorrow | nnoremap <F5> :edit<CR> | ":SyntasticCheck"
if &diff
  autocmd VimEnter * syntax off | SyntasticToggleMode
endif

" toggle git diff for a buffer
function! GitDiffToggle()
  if &diff
    diffoff!
"   set background=light
"   colorscheme Tomorrow
    nnoremap <F5> :edit<CR>
    :bd
    :SyntasticCheck
  else
    :SyntasticToggleMode
    :Gdiff HEAD
  endif
endfunction
nnoremap <F7> :call GitDiffToggle()<CR>

" let vim see bash aliases when executing commands
let $BASH_ENV="$DOTFILES_HOME/.bash_aliases"