# Dot Files
This is an opinionated collection of useful dot files (`bash` only) in the context of Kubernetes (K8s). They can be easily integrated into your local machine setup as they are free of personal information.

## Prerequisites
The setup was tested on Mac and Ubuntu. Your user should correspond to your user in [GitHub](https://github.com) (e.g. plkokanov) and you should have maintained your full name, e-mail address, and your public keys in your GitHub user profile.

## Integration
To integrate the dot files into your local machine, first clone this repo to the folder where it should reside in the future (we use `~/git/dotfiles` here). Then source the dot files `.bash_profile` respectively `.bashrc` from your own initialization files.

Add to your local `.bash_profile` (replace path as needed):

``` sh
# source bash_profile from dotfiles
source "$HOME/git/dotfiles/.bash_profile"
```

Add to your local `.bashrc` (replace path as needed):

``` sh
# source bashrc from dotfiles
source "$HOME/git/dotfiles/.bashrc"
```

The dot files will also modify [`XDG_CONFIG_HOME`](https://specifications.freedesktop.org/basedir-spec/basedir-spec-0.6.html), the configuration home to many tools including git. However, and here is the caveat, on your own local machine this would be unintended/conflicting with your personal configuration, so the dot files won't do it there. But since the dot files contain also many useful git defaults (and carry your identity to remote machines when you `ssh` into them), it would be great to combine your local git configuration (where you e.g. use the key chain on Macs or plug in native diff/merge tools) with the dot files git configuration. Luckily, git configuration supports `include`s.

Add to your local `.gitconfig` (replace path as needed):

``` sh
# OS unspecific settings
[include]
  path = ~/git/dotfiles/.config/git/config

# OS specific settings for credentials management or native diff/merge tools
[credential]
  helper = osxkeychain
...
```

## Update
As simple as `git pull`.
