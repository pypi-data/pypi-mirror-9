# Bind fzsl to the specified keystroke.  This will allow a single
# keybinding to execute fzsl from the current directory.  The highest
# priority rule will be used to scan.
#
# Parameters:
#   $1  - If specified, the readline code for the keybinding that will
#         launch fzsl.  Defaults to ctrl+p (\C-p).
__fzsl_bind_default_matching() {
    local binding=${1:-\C-p}

    if set -o | grep -q 'vi\s*on'; then
        bind '"\C-x\C-E": shell-expand-line'
        bind '"\C-x\C-R": redraw-current-line'
        bind "'${binding}': '\e\$a \eddi\$(fzsl)\C-x\C-E\e0Pa \exddi\n\epa \C-x\C-R'"
        bind -m vi-command "'${binding}': 'i${binding}'"
    else
        bind '"\eR": redraw-current-line'
        bind "${binding}': ' \C-u \C-a\C-k\$(fzsl)\e\C-e\C-y\C-a\C-y\ey\C-a\C-k\n\C-y\C-e\eR \C-h'"
    fi
}

# Setup an alias for fuzzy cd.  Running 'fzcd' will launch the
# ui with only directories as options and cd to the selected
# path on completion
#
# Parameters:
#   $1  - Rule to use for fuzzy directory matching.  Defaults to dirs-only
__fzsl_create_fzcd() {
    local rule=${1:-dirs-only}

    fzcd() {
        local dir=$(fzsl --rule dirs-only)
        [ -n "${dir}" ] && cd ${dir}
    }
}

# Echo the top directory of a git tree.  If currently in a submodule,
# this assumes that 'git rev-parse --show-gitdir' will return a
# subdirectory of the top gitdir which is named '.git'
__fzsl_top_gitdir() {
    local d=$(git rev-parse --git-dir 2>/dev/null)
    [ $? -ne 0 ] && return

    d=$(readlink -m "${d}")
    d=${d%/.git*}
    echo "${d}"
}


# Check if the root of the current git tree has submodules.
__fzsl_have_git_submodules() {
    local top_gitdir=$(__fzsl_top_gitdir)

    [ $? -ne 0 ] && return 1

    [ -s "${top_gitdir}/.gitmodules" ]
}

# Echo the path to all files within the git repository and every submodule
# with paths rooted at the top-level git repository
#
# Parameters:
#  $*   - Extra parameters to pass to git ls-files.
__fzsl_scan_git_with_submodules() {
    local top_gitdir=$(__fzsl_top_gitdir)

    [ -z "${top_gitdir}" ] && return

    pushd "${top_gitdir}" &> /dev/null
    echo $top_gitdir

    git ls-files $*
    git submodule foreach --quiet \
        "for f in \$(git ls-files $*); do echo \${path}/\${f};done"

    popd &> /dev/null
}

