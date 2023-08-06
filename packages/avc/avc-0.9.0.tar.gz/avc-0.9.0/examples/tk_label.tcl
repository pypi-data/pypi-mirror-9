#!/bin/sh
# the next line restarts using wish\
exec wish "$0" "$@" 

if {![info exists vTcl(sourcing)]} {

    package require Tk
    switch $tcl_platform(platform) {
	windows {
            option add *Button.padY 0
	}
	default {
            option add *Scrollbar.width 10
            option add *Scrollbar.highlightThickness 0
            option add *Scrollbar.elementBorderWidth 2
            option add *Scrollbar.borderWidth 2
	}
    }
    
}

#############################################################################
# Visual Tcl v1.60 Project
#


#################################
# VTCL LIBRARY PROCEDURES
#

if {![info exists vTcl(sourcing)]} {
#############################################################################
## Library Procedure:  Window

proc ::Window {args} {
    ## This procedure may be used free of restrictions.
    ##    Exception added by Christian Gavin on 08/08/02.
    ## Other packages and widget toolkits have different licensing requirements.
    ##    Please read their license agreements for details.

    global vTcl
    foreach {cmd name newname} [lrange $args 0 2] {}
    set rest    [lrange $args 3 end]
    if {$name == "" || $cmd == ""} { return }
    if {$newname == ""} { set newname $name }
    if {$name == "."} { wm withdraw $name; return }
    set exists [winfo exists $newname]
    switch $cmd {
        show {
            if {$exists} {
                wm deiconify $newname
            } elseif {[info procs vTclWindow$name] != ""} {
                eval "vTclWindow$name $newname $rest"
            }
            if {[winfo exists $newname] && [wm state $newname] == "normal"} {
                vTcl:FireEvent $newname <<Show>>
            }
        }
        hide    {
            if {$exists} {
                wm withdraw $newname
                vTcl:FireEvent $newname <<Hide>>
                return}
        }
        iconify { if $exists {wm iconify $newname; return} }
        destroy { if $exists {destroy $newname; return} }
    }
}
#############################################################################
## Library Procedure:  vTcl:DefineAlias

proc ::vTcl:DefineAlias {target alias widgetProc top_or_alias cmdalias} {
    ## This procedure may be used free of restrictions.
    ##    Exception added by Christian Gavin on 08/08/02.
    ## Other packages and widget toolkits have different licensing requirements.
    ##    Please read their license agreements for details.

    global widget
    set widget($alias) $target
    set widget(rev,$target) $alias
    if {$cmdalias} {
        interp alias {} $alias {} $widgetProc $target
    }
    if {$top_or_alias != ""} {
        set widget($top_or_alias,$alias) $target
        if {$cmdalias} {
            interp alias {} $top_or_alias.$alias {} $widgetProc $target
        }
    }
}
#############################################################################
## Library Procedure:  vTcl:DoCmdOption

proc ::vTcl:DoCmdOption {target cmd} {
    ## This procedure may be used free of restrictions.
    ##    Exception added by Christian Gavin on 08/08/02.
    ## Other packages and widget toolkits have different licensing requirements.
    ##    Please read their license agreements for details.

    ## menus are considered toplevel windows
    set parent $target
    while {[winfo class $parent] == "Menu"} {
        set parent [winfo parent $parent]
    }

    regsub -all {\%widget} $cmd $target cmd
    regsub -all {\%top} $cmd [winfo toplevel $parent] cmd

    uplevel #0 [list eval $cmd]
}
#############################################################################
## Library Procedure:  vTcl:FireEvent

proc ::vTcl:FireEvent {target event {params {}}} {
    ## This procedure may be used free of restrictions.
    ##    Exception added by Christian Gavin on 08/08/02.
    ## Other packages and widget toolkits have different licensing requirements.
    ##    Please read their license agreements for details.

    ## The window may have disappeared
    if {![winfo exists $target]} return
    ## Process each binding tag, looking for the event
    foreach bindtag [bindtags $target] {
        set tag_events [bind $bindtag]
        set stop_processing 0
        foreach tag_event $tag_events {
            if {$tag_event == $event} {
                set bind_code [bind $bindtag $tag_event]
                foreach rep "\{%W $target\} $params" {
                    regsub -all [lindex $rep 0] $bind_code [lindex $rep 1] bind_code
                }
                set result [catch {uplevel #0 $bind_code} errortext]
                if {$result == 3} {
                    ## break exception, stop processing
                    set stop_processing 1
                } elseif {$result != 0} {
                    bgerror $errortext
                }
                break
            }
        }
        if {$stop_processing} {break}
    }
}
#############################################################################
## Library Procedure:  vTcl:Toplevel:WidgetProc

proc ::vTcl:Toplevel:WidgetProc {w args} {
    ## This procedure may be used free of restrictions.
    ##    Exception added by Christian Gavin on 08/08/02.
    ## Other packages and widget toolkits have different licensing requirements.
    ##    Please read their license agreements for details.

    if {[llength $args] == 0} {
        ## If no arguments, returns the path the alias points to
        return $w
    }
    set command [lindex $args 0]
    set args [lrange $args 1 end]
    switch -- [string tolower $command] {
        "setvar" {
            foreach {varname value} $args {}
            if {$value == ""} {
                return [set ::${w}::${varname}]
            } else {
                return [set ::${w}::${varname} $value]
            }
        }
        "hide" - "show" {
            Window [string tolower $command] $w
        }
        "showmodal" {
            ## modal dialog ends when window is destroyed
            Window show $w; raise $w
            grab $w; tkwait window $w; grab release $w
        }
        "startmodal" {
            ## ends when endmodal called
            Window show $w; raise $w
            set ::${w}::_modal 1
            grab $w; tkwait variable ::${w}::_modal; grab release $w
        }
        "endmodal" {
            ## ends modal dialog started with startmodal, argument is var name
            set ::${w}::_modal 0
            Window hide $w
        }
        default {
            uplevel $w $command $args
        }
    }
}
#############################################################################
## Library Procedure:  vTcl:WidgetProc

proc ::vTcl:WidgetProc {w args} {
    ## This procedure may be used free of restrictions.
    ##    Exception added by Christian Gavin on 08/08/02.
    ## Other packages and widget toolkits have different licensing requirements.
    ##    Please read their license agreements for details.

    if {[llength $args] == 0} {
        ## If no arguments, returns the path the alias points to
        return $w
    }

    set command [lindex $args 0]
    set args [lrange $args 1 end]
    uplevel $w $command $args
}
#############################################################################
## Library Procedure:  vTcl:toplevel

proc ::vTcl:toplevel {args} {
    ## This procedure may be used free of restrictions.
    ##    Exception added by Christian Gavin on 08/08/02.
    ## Other packages and widget toolkits have different licensing requirements.
    ##    Please read their license agreements for details.

    uplevel #0 eval toplevel $args
    set target [lindex $args 0]
    namespace eval ::$target {set _modal 0}
}
}


if {[info exists vTcl(sourcing)]} {

proc vTcl:project:info {} {
    set base .window1
    namespace eval ::widgets::$base {
        set set,origin 1
        set set,size 1
        set runvisible 1
    }
    namespace eval ::widgets::$base.label1 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label2 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label3 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label4 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label5 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label6 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label7 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label8 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label9 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label10 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.label11 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.cpd49 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.bool_value__2 {
        array set save {-disabledforeground 1}
    }
    namespace eval ::widgets::$base.bool_value__1 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.cpd52 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.float_value__1 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.float_value__2 {
        array set save {-disabledforeground 1}
    }
    namespace eval ::widgets::$base.cpd53 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.int_value__1 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.int_value__2 {
        array set save {-disabledforeground 1}
    }
    namespace eval ::widgets::$base.cpd54 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.list_value__1 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.list_value__2 {
        array set save {-disabledforeground 1}
    }
    namespace eval ::widgets::$base.cpd56 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.str_value__1 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.str_value__2 {
        array set save {-disabledforeground 1}
    }
    namespace eval ::widgets::$base.cpd57 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.cpd58 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.tuple_value__1 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.tuple_value__2 {
        array set save {-disabledforeground 1}
    }
    namespace eval ::widgets::$base.obj_value__1 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$base.obj_value__2 {
        array set save {-disabledforeground 1}
    }
    namespace eval ::widgets_bindings {
        set tagslist _TopLevel
    }
    namespace eval ::vTcl::modules::main {
        set procs {
            init
            main
        }
        set compounds {
        }
        set projectType single
    }
}
}

#################################
# USER DEFINED PROCEDURES
#
#############################################################################
## Procedure:  main

proc ::main {argc argv} {}

#############################################################################
## Initialization Procedure:  init

proc ::init {argc argv} {}

init $argc $argv

#################################
# VTCL GENERATED GUI PROCEDURES
#

proc vTclWindow. {base} {
    if {$base == ""} {
        set base .
    }
    ###################
    # CREATING WIDGETS
    ###################
    wm focusmodel $top passive
    wm geometry $top 1x1+0+0; update
    wm maxsize $top 1265 994
    wm minsize $top 1 1
    wm overrideredirect $top 0
    wm resizable $top 1 1
    wm withdraw $top
    wm title $top "vtcl.tcl"
    bindtags $top "$top Vtcl.tcl all"
    vTcl:FireEvent $top <<Create>>
    wm protocol $top WM_DELETE_WINDOW "vTcl:FireEvent $top <<DeleteWindow>>"

    ###################
    # SETTING GEOMETRY
    ###################

    vTcl:FireEvent $base <<Ready>>
}

proc vTclWindow.window1 {base} {
    if {$base == ""} {
        set base .window1
    }
    if {[winfo exists $base]} {
        wm deiconify $base; return
    }
    set top $base
    ###################
    # CREATING WIDGETS
    ###################
    vTcl:toplevel $top -class Toplevel \
        -highlightcolor black 
    wm focusmodel $top passive
    wm geometry $top 646x200+63+403; update
    wm maxsize $top 1265 994
    wm minsize $top 1 1
    wm overrideredirect $top 0
    wm resizable $top 1 1
    wm deiconify $top
    wm title $top "AVC Tk label example"
    vTcl:DefineAlias "$top" "Toplevel1" vTcl:Toplevel:WidgetProc "" 1
    bindtags $top "$top Toplevel all _TopLevel"
    vTcl:FireEvent $top <<Create>>
    wm protocol $top WM_DELETE_WINDOW "vTcl:FireEvent $top <<DeleteWindow>>"

    label $top.label1 \
        -disabledforeground #a1a4a1 -text {Control type} 
    vTcl:DefineAlias "$top.label1" "Label1" vTcl:WidgetProc "Toplevel1" 1
    label $top.label2 \
        -disabledforeground #a1a4a1 -text {Format string} 
    vTcl:DefineAlias "$top.label2" "Label2" vTcl:WidgetProc "Toplevel1" 1
    label $top.label3 \
        -disabledforeground #a1a4a1 -text {Label with format} 
    vTcl:DefineAlias "$top.label3" "Label3" vTcl:WidgetProc "Toplevel1" 1
    label $top.label4 \
        -disabledforeground #a1a4a1 -text {Label without format} 
    vTcl:DefineAlias "$top.label4" "Label4" vTcl:WidgetProc "Toplevel1" 1
    label $top.label5 \
        -disabledforeground #a1a4a1 -text boolean 
    vTcl:DefineAlias "$top.label5" "Label5" vTcl:WidgetProc "Toplevel1" 1
    label $top.label6 \
        -disabledforeground #a1a4a1 -text float 
    vTcl:DefineAlias "$top.label6" "Label6" vTcl:WidgetProc "Toplevel1" 1
    label $top.label7 \
        -disabledforeground #a1a4a1 -text integer 
    vTcl:DefineAlias "$top.label7" "Label7" vTcl:WidgetProc "Toplevel1" 1
    label $top.label8 \
        -disabledforeground #a1a4a1 -text list 
    vTcl:DefineAlias "$top.label8" "Label8" vTcl:WidgetProc "Toplevel1" 1
    label $top.label9 \
        -disabledforeground #a1a4a1 -text string 
    vTcl:DefineAlias "$top.label9" "Label9" vTcl:WidgetProc "Toplevel1" 1
    label $top.label10 \
        -disabledforeground #a1a4a1 -text tuple 
    vTcl:DefineAlias "$top.label10" "Label10" vTcl:WidgetProc "Toplevel1" 1
    label $top.label11 \
        -disabledforeground #a1a4a1 -text {object with attributes x=1,y=2} 
    vTcl:DefineAlias "$top.label11" "Label11" vTcl:WidgetProc "Toplevel1" 1
    label $top.cpd49 \
        -disabledforeground #a1a4a1 -text %d 
    vTcl:DefineAlias "$top.cpd49" "Label12" vTcl:WidgetProc "Toplevel1" 1
    label $top.bool_value__2 \
        -disabledforeground #a1a4a1 
    vTcl:DefineAlias "$top.bool_value__2" "Label14" vTcl:WidgetProc "Toplevel1" 1
    label $top.bool_value__1 \
        -disabledforeground #a1a4a1 -text %d 
    vTcl:DefineAlias "$top.bool_value__1" "Label13" vTcl:WidgetProc "Toplevel1" 1
    label $top.cpd52 \
        -disabledforeground #a1a4a1 -text %f 
    vTcl:DefineAlias "$top.cpd52" "Label15" vTcl:WidgetProc "Toplevel1" 1
    label $top.float_value__1 \
        -disabledforeground #a1a4a1 -text %f 
    vTcl:DefineAlias "$top.float_value__1" "Label16" vTcl:WidgetProc "Toplevel1" 1
    label $top.float_value__2 \
        -disabledforeground #a1a4a1 
    vTcl:DefineAlias "$top.float_value__2" "Label17" vTcl:WidgetProc "Toplevel1" 1
    label $top.cpd53 \
        -disabledforeground #a1a4a1 -text %d 
    vTcl:DefineAlias "$top.cpd53" "Label18" vTcl:WidgetProc "Toplevel1" 1
    label $top.int_value__1 \
        -disabledforeground #a1a4a1 -text %d 
    vTcl:DefineAlias "$top.int_value__1" "Label19" vTcl:WidgetProc "Toplevel1" 1
    label $top.int_value__2 \
        -disabledforeground #a1a4a1 
    vTcl:DefineAlias "$top.int_value__2" "Label20" vTcl:WidgetProc "Toplevel1" 1
    label $top.cpd54 \
        -disabledforeground #a1a4a1 -text %d,%d,%d 
    vTcl:DefineAlias "$top.cpd54" "Label21" vTcl:WidgetProc "Toplevel1" 1
    label $top.list_value__1 \
        -disabledforeground #a1a4a1 -text %d,%d,%d 
    vTcl:DefineAlias "$top.list_value__1" "Label22" vTcl:WidgetProc "Toplevel1" 1
    label $top.list_value__2 \
        -disabledforeground #a1a4a1 
    vTcl:DefineAlias "$top.list_value__2" "Label23" vTcl:WidgetProc "Toplevel1" 1
    label $top.cpd56 \
        -disabledforeground #a1a4a1 -text %s 
    vTcl:DefineAlias "$top.cpd56" "Label24" vTcl:WidgetProc "Toplevel1" 1
    label $top.str_value__1 \
        -disabledforeground #a1a4a1 -text %s 
    vTcl:DefineAlias "$top.str_value__1" "Label25" vTcl:WidgetProc "Toplevel1" 1
    label $top.str_value__2 \
        -disabledforeground #a1a4a1 
    vTcl:DefineAlias "$top.str_value__2" "Label26" vTcl:WidgetProc "Toplevel1" 1
    label $top.cpd57 \
        -disabledforeground #a1a4a1 -text %d,%d,%d 
    vTcl:DefineAlias "$top.cpd57" "Label27" vTcl:WidgetProc "Toplevel1" 1
    label $top.cpd58 \
        -disabledforeground #a1a4a1 -text %(x)d,%(y)d 
    vTcl:DefineAlias "$top.cpd58" "Label28" vTcl:WidgetProc "Toplevel1" 1
    label $top.tuple_value__1 \
        -disabledforeground #a1a4a1 -text %d,%d,%d 
    vTcl:DefineAlias "$top.tuple_value__1" "Label29" vTcl:WidgetProc "Toplevel1" 1
    label $top.tuple_value__2 \
        -disabledforeground #a1a4a1 
    vTcl:DefineAlias "$top.tuple_value__2" "Label30" vTcl:WidgetProc "Toplevel1" 1
    label $top.obj_value__1 \
        -disabledforeground #a1a4a1 -text %(x)d,%(y)d 
    vTcl:DefineAlias "$top.obj_value__1" "Label31" vTcl:WidgetProc "Toplevel1" 1
    label $top.obj_value__2 \
        -disabledforeground #a1a4a1 
    vTcl:DefineAlias "$top.obj_value__2" "Label32" vTcl:WidgetProc "Toplevel1" 1
    ###################
    # SETTING GEOMETRY
    ###################
    grid rowconf $top 1 -minsize 4
    grid $top.label1 \
        -in $top -column 0 -row 0 -columnspan 1 -rowspan 1 
    grid $top.label2 \
        -in $top -column 1 -row 0 -columnspan 1 -rowspan 1 
    grid $top.label3 \
        -in $top -column 2 -row 0 -columnspan 1 -rowspan 1 
    grid $top.label4 \
        -in $top -column 3 -row 0 -columnspan 1 -rowspan 1 
    grid $top.label5 \
        -in $top -column 0 -row 1 -columnspan 1 -rowspan 1 
    grid $top.label6 \
        -in $top -column 0 -row 2 -columnspan 1 -rowspan 1 
    grid $top.label7 \
        -in $top -column 0 -row 3 -columnspan 1 -rowspan 1 
    grid $top.label8 \
        -in $top -column 0 -row 4 -columnspan 1 -rowspan 1 
    grid $top.label9 \
        -in $top -column 0 -row 5 -columnspan 1 -rowspan 1 
    grid $top.label10 \
        -in $top -column 0 -row 6 -columnspan 1 -rowspan 1 
    grid $top.label11 \
        -in $top -column 0 -row 7 -columnspan 1 -rowspan 1 
    grid $top.cpd49 \
        -in $top -column 1 -row 1 -columnspan 1 -rowspan 1 
    grid $top.bool_value__2 \
        -in $top -column 3 -row 1 -columnspan 1 -rowspan 1 
    grid $top.bool_value__1 \
        -in $top -column 2 -row 1 -columnspan 1 -rowspan 1 
    grid $top.cpd52 \
        -in $top -column 1 -row 2 -columnspan 1 -rowspan 1 
    grid $top.float_value__1 \
        -in $top -column 2 -row 2 -columnspan 1 -rowspan 1 
    grid $top.float_value__2 \
        -in $top -column 3 -row 2 -columnspan 1 -rowspan 1 
    grid $top.cpd53 \
        -in $top -column 1 -row 3 -columnspan 1 -rowspan 1 
    grid $top.int_value__1 \
        -in $top -column 2 -row 3 -columnspan 1 -rowspan 1 
    grid $top.int_value__2 \
        -in $top -column 3 -row 3 -columnspan 1 -rowspan 1 
    grid $top.cpd54 \
        -in $top -column 1 -row 4 -columnspan 1 -rowspan 1 
    grid $top.list_value__1 \
        -in $top -column 2 -row 4 -columnspan 1 -rowspan 1 
    grid $top.list_value__2 \
        -in $top -column 3 -row 4 -columnspan 1 -rowspan 1 
    grid $top.cpd56 \
        -in $top -column 1 -row 5 -columnspan 1 -rowspan 1 
    grid $top.str_value__1 \
        -in $top -column 2 -row 5 -columnspan 1 -rowspan 1 
    grid $top.str_value__2 \
        -in $top -column 3 -row 5 -columnspan 1 -rowspan 1 
    grid $top.cpd57 \
        -in $top -column 1 -row 6 -columnspan 1 -rowspan 1 
    grid $top.cpd58 \
        -in $top -column 1 -row 7 -columnspan 1 -rowspan 1 
    grid $top.tuple_value__1 \
        -in $top -column 2 -row 6 -columnspan 1 -rowspan 1 
    grid $top.tuple_value__2 \
        -in $top -column 3 -row 6 -columnspan 1 -rowspan 1 
    grid $top.obj_value__1 \
        -in $top -column 2 -row 7 -columnspan 1 -rowspan 1 
    grid $top.obj_value__2 \
        -in $top -column 3 -row 7 -columnspan 1 -rowspan 1 

    vTcl:FireEvent $base <<Ready>>
}

#############################################################################
## Binding tag:  _TopLevel

bind "_TopLevel" <<Create>> {
    if {![info exists _topcount]} {set _topcount 0}; incr _topcount
}
bind "_TopLevel" <<DeleteWindow>> {
    if {[set ::%W::_modal]} {
                vTcl:Toplevel:WidgetProc %W endmodal
            } else {
                destroy %W; if {$_topcount == 0} {exit}
            }
}
bind "_TopLevel" <Destroy> {
    if {[winfo toplevel %W] == "%W"} {incr _topcount -1}
}

Window show .
Window show .window1

main $argc $argv
