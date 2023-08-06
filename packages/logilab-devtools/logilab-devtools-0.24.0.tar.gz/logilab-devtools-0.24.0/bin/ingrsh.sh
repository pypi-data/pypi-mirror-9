# switch you work environment to a guestrepo shell
# set PYTHONPATH and CDPATH accordingly
#
# usage: ingrsh [name]
#
# With no argument it list all available grshell
if [ -z "$GUESTREPODIR" ]; then
    export GUESTREPODIR="$HOME/hg/grshells/"
fi

ingrsh() {
    if [ $# -eq 0 ]
    then
        # the leading = disable potential alias
        ls -1 $GUESTREPODIR | sed 's/^grshell-//'
        return 0
    fi
    grsh_path=${GUESTREPODIR}/grshell-$1
    if [ ! -d "$grsh_path" ]
    then
        echo no such guestrepo shell: '"'$grsh_path'"' >&2;
        echo 'possible values are:' >&2;
        ls -1 $GUESTREPODIR | sed 's/^grshell-/    /' >&2;
        return 1;
    fi
    export GRROOT=$grsh_path
    export PYTHONPATH=$grsh_path;
    export CDPATH=$grsh_path;
    export GRNAME=$1;
    export CW_INSTANCES_DIR=$grsh_path/etc
    export PS1='\[\e]0;\u@\h: \w\a\]\u@\h:$( hg status -R $CDPATH -q 2>&1 | egrep -q ".+" && echo "\[\033[01;31m\]" || echo "\[\033[01;32m\]" )[$GRNAME:$( hg branch -R $CDPATH )]/${PWD:${#CDPATH}}\[\033[01;00m\]\$ '
    cd $grsh_path;
}

_ingrsh() {
  cur=$2
  COMPREPLY=( $( compgen -W "$( ingrsh )" -- "$cur" ) )
}

complete -F _ingrsh ingrsh

