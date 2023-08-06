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
    set base .root
    namespace eval ::widgets::$base {
        set set,origin 1
        set set,size 1
        set runvisible 1
    }
    namespace eval ::widgets::$base.row0 {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_3_0 $base.row0
    namespace eval ::widgets::$site_3_0.label1 {
        array set save {-text 1}
    }
    namespace eval ::widgets::$site_3_0.label3 {
        array set save {-text 1}
    }
    namespace eval ::widgets::$site_3_0.label2 {
        array set save {-text 1}
    }
    namespace eval ::widgets::$base.row1 {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_3_0 $base.row1
    namespace eval ::widgets::$site_3_0.label4 {
        array set save {-text 1}
    }
    namespace eval ::widgets::$site_3_0.boolean1__label {
        array set save {-text 1}
    }
    namespace eval ::widgets::$site_3_0.boolean1__button {
        array set save {-text 1}
    }
    namespace eval ::widgets::$base.row2 {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_3_0 $base.row2
    namespace eval ::widgets::$site_3_0.label5 {
        array set save {-text 1}
    }
    namespace eval ::widgets::$site_3_0.boolean2__label {
        array set save {-text 1}
    }
    namespace eval ::widgets::$site_3_0.boolean2__checkbutton {
        array set save {-text 1 -variable 1}
    }
    namespace eval ::widgets::$base.row3 {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_3_0 $base.row3
    namespace eval ::widgets::$site_3_0.label6 {
        array set save {-text 1}
    }
    namespace eval ::widgets::$site_3_0.radio__label {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$site_3_0.frame_radio {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_4_0 $site_3_0.frame_radio
    namespace eval ::widgets::$site_4_0.radio__radiobutton0 {
        array set save {-disabledforeground 1 -text 1 -value 1 -variable 1}
    }
    namespace eval ::widgets::$site_4_0.radio__radiobutton2 {
        array set save {-disabledforeground 1 -text 1 -value 1 -variable 1}
    }
    namespace eval ::widgets::$site_4_0.radio__radiobutton1 {
        array set save {-disabledforeground 1 -text 1 -value 1 -variable 1}
    }
    namespace eval ::widgets::$base.row4 {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_3_0 $base.row4
    namespace eval ::widgets::$site_3_0.label7 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$site_3_0.integer__label {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$site_3_0.frame_integer {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_4_0 $site_3_0.frame_integer
    namespace eval ::widgets::$site_4_0.integer__spinbox {
        array set save {-activebackground 1 -disabledforeground 1 -foreground 1 -from 1 -highlightcolor 1 -increment 1 -insertbackground 1 -selectbackground 1 -selectforeground 1 -to 1 -width 1}
    }
    namespace eval ::widgets::$site_4_0.integer__hscale {
        array set save {-bigincrement 1 -orient 1 -resolution 1 -variable 1}
    }
    namespace eval ::widgets::$site_4_0.integer__entry {
        array set save {-background 1 -disabledforeground 1 -insertbackground 1 -textvariable 1 -width 1}
    }
    namespace eval ::widgets::$base.row5 {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_3_0 $base.row5
    namespace eval ::widgets::$site_3_0.label8 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$site_3_0.float__label {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$site_3_0.frame_float {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_4_0 $site_3_0.frame_float
    namespace eval ::widgets::$site_4_0.float__spinbox {
        array set save {-activebackground 1 -disabledforeground 1 -foreground 1 -from 1 -highlightcolor 1 -increment 1 -insertbackground 1 -selectbackground 1 -selectforeground 1 -to 1 -width 1}
    }
    namespace eval ::widgets::$site_4_0.float__hscale {
        array set save {-bigincrement 1 -from 1 -orient 1 -resolution 1 -variable 1}
    }
    namespace eval ::widgets::$site_4_0.float__entry {
        array set save {-background 1 -disabledforeground 1 -insertbackground 1 -textvariable 1 -width 1}
    }
    namespace eval ::widgets::$base.row6 {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_3_0 $base.row6
    namespace eval ::widgets::$site_3_0.label9 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$site_3_0.string__label {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$site_3_0.string__entry {
        array set save {-background 1 -disabledforeground 1 -insertbackground 1 -textvariable 1}
    }
    namespace eval ::widgets::$base.row7 {
        array set save {-borderwidth 1 -height 1 -relief 1 -width 1}
    }
    set site_3_0 $base.row7
    namespace eval ::widgets::$site_3_0.label10 {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$site_3_0.textview__label {
        array set save {-disabledforeground 1 -text 1}
    }
    namespace eval ::widgets::$site_3_0.textview__text {
        array set save {-background 1 -foreground 1 -height 1 -highlightcolor 1 -insertbackground 1 -selectbackground 1 -selectforeground 1 -width 1 -wrap 1}
    }
    namespace eval ::widgets_bindings {
        set tagslist _TopLevel
    }
    namespace eval ::vTcl::modules::main {
        set procs {
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

proc vTclWindow.root {base} {
    if {$base == ""} {
        set base .root
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
    wm geometry $top 609x318+53+247; update
    wm maxsize $top 1265 994
    wm minsize $top 1 1
    wm overrideredirect $top 0
    wm resizable $top 1 1
    wm deiconify $top
    wm title $top "AVC Tk showcase example"
    vTcl:DefineAlias "$top" "Toplevel1" vTcl:Toplevel:WidgetProc "" 1
    bindtags $top "$top Toplevel all _TopLevel"
    vTcl:FireEvent $top <<Create>>
    wm protocol $top WM_DELETE_WINDOW "vTcl:FireEvent $top <<DeleteWindow>>"

    frame $top.row0 \
        -borderwidth 2 -relief groove -height 35 -width 125 
    vTcl:DefineAlias "$top.row0" "Frame1" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.row0
    label $site_3_0.label1 \
        -text {Control Type} 
    vTcl:DefineAlias "$site_3_0.label1" "Label1" vTcl:WidgetProc "Toplevel1" 1
    label $site_3_0.label3 \
        -text {Control Value} 
    vTcl:DefineAlias "$site_3_0.label3" "Label3" vTcl:WidgetProc "Toplevel1" 1
    label $site_3_0.label2 \
        -text Widgets 
    vTcl:DefineAlias "$site_3_0.label2" "Label2" vTcl:WidgetProc "Toplevel1" 1
    pack $site_3_0.label1 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side left 
    pack $site_3_0.label3 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side right 
    pack $site_3_0.label2 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side top 
    frame $top.row1 \
        -borderwidth 2 -relief groove -height 75 -width 125 
    vTcl:DefineAlias "$top.row1" "Frame2" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.row1
    label $site_3_0.label4 \
        -text boolean1 
    vTcl:DefineAlias "$site_3_0.label4" "Label4" vTcl:WidgetProc "Toplevel1" 1
    label $site_3_0.boolean1__label \
        -text boolean1 
    vTcl:DefineAlias "$site_3_0.boolean1__label" "Label5" vTcl:WidgetProc "Toplevel1" 1
    button $site_3_0.boolean1__button \
        -text button 
    vTcl:DefineAlias "$site_3_0.boolean1__button" "Button1" vTcl:WidgetProc "Toplevel1" 1
    pack $site_3_0.label4 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side left 
    pack $site_3_0.boolean1__label \
        -in $site_3_0 -anchor center -expand 0 -fill none -side right 
    pack $site_3_0.boolean1__button \
        -in $site_3_0 -anchor center -expand 0 -fill none -side top 
    frame $top.row2 \
        -borderwidth 2 -relief groove -height 75 -width 125 
    vTcl:DefineAlias "$top.row2" "Frame3" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.row2
    label $site_3_0.label5 \
        -text boolean2 
    vTcl:DefineAlias "$site_3_0.label5" "Label6" vTcl:WidgetProc "Toplevel1" 1
    label $site_3_0.boolean2__label \
        -text boolean2 
    vTcl:DefineAlias "$site_3_0.boolean2__label" "Label7" vTcl:WidgetProc "Toplevel1" 1
    checkbutton $site_3_0.boolean2__checkbutton \
        -text {check button} -variable "$top\::boolean2__checkbutton" 
    vTcl:DefineAlias "$site_3_0.boolean2__checkbutton" "Checkbutton1" vTcl:WidgetProc "Toplevel1" 1
    pack $site_3_0.label5 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side left 
    pack $site_3_0.boolean2__label \
        -in $site_3_0 -anchor center -expand 0 -fill none -side right 
    pack $site_3_0.boolean2__checkbutton \
        -in $site_3_0 -anchor center -expand 0 -fill none -side top 
    frame $top.row3 \
        -borderwidth 2 -relief groove -height 184 -width 125 
    vTcl:DefineAlias "$top.row3" "Frame4" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.row3
    label $site_3_0.label6 \
        -text index 
    vTcl:DefineAlias "$site_3_0.label6" "Label8" vTcl:WidgetProc "Toplevel1" 1
    label $site_3_0.radio__label \
        -disabledforeground #a1a4a1 -text index 
    vTcl:DefineAlias "$site_3_0.radio__label" "Label9" vTcl:WidgetProc "Toplevel1" 1
    frame $site_3_0.frame_radio \
        -borderwidth 2 -relief groove -height 75 -width 125 
    vTcl:DefineAlias "$site_3_0.frame_radio" "Frame6" vTcl:WidgetProc "Toplevel1" 1
    set site_4_0 $site_3_0.frame_radio
    radiobutton $site_4_0.radio__radiobutton0 \
        -disabledforeground #a1a4a1 -text {radio button 0} -value 0 \
        -variable selectedButton 
    vTcl:DefineAlias "$site_4_0.radio__radiobutton0" "Radiobutton1" vTcl:WidgetProc "Toplevel1" 1
    radiobutton $site_4_0.radio__radiobutton2 \
        -disabledforeground #a1a4a1 -text {radio button 2} -value 2 \
        -variable selectedButton 
    vTcl:DefineAlias "$site_4_0.radio__radiobutton2" "Radiobutton2" vTcl:WidgetProc "Toplevel1" 1
    radiobutton $site_4_0.radio__radiobutton1 \
        -disabledforeground #a1a4a1 -text {radio button 1} -value 1 \
        -variable selectedButton 
    vTcl:DefineAlias "$site_4_0.radio__radiobutton1" "Radiobutton3" vTcl:WidgetProc "Toplevel1" 1
    pack $site_4_0.radio__radiobutton0 \
        -in $site_4_0 -anchor center -expand 0 -fill none -side left 
    pack $site_4_0.radio__radiobutton2 \
        -in $site_4_0 -anchor center -expand 0 -fill none -side right 
    pack $site_4_0.radio__radiobutton1 \
        -in $site_4_0 -anchor center -expand 0 -fill none -side top 
    pack $site_3_0.label6 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side left 
    pack $site_3_0.radio__label \
        -in $site_3_0 -anchor center -expand 0 -fill none -side right 
    pack $site_3_0.frame_radio \
        -in $site_3_0 -anchor center -expand 0 -fill none -side top 
    frame $top.row4 \
        -borderwidth 2 -relief groove -height 75 -width 125 
    vTcl:DefineAlias "$top.row4" "Frame5" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.row4
    label $site_3_0.label7 \
        -disabledforeground #a1a4a1 -text integer 
    vTcl:DefineAlias "$site_3_0.label7" "Label10" vTcl:WidgetProc "Toplevel1" 1
    label $site_3_0.integer__label \
        -disabledforeground #a1a4a1 -text integer 
    vTcl:DefineAlias "$site_3_0.integer__label" "Label11" vTcl:WidgetProc "Toplevel1" 1
    frame $site_3_0.frame_integer \
        -borderwidth 2 -relief groove -height 75 -width 269 
    vTcl:DefineAlias "$site_3_0.frame_integer" "Frame7" vTcl:WidgetProc "Toplevel1" 1
    set site_4_0 $site_3_0.frame_integer
    spinbox $site_4_0.integer__spinbox \
        -activebackground #f7fbf7 -disabledforeground #a1a4a1 \
        -foreground black -from 0.0 -highlightcolor black -increment 1.0 \
        -insertbackground black -selectbackground #c1c5c1 \
        -selectforeground black -to 100.0 -width 6 
    vTcl:DefineAlias "$site_4_0.integer__spinbox" "Spinbox1" vTcl:WidgetProc "Toplevel1" 1
    scale $site_4_0.integer__hscale \
        -bigincrement 0.0 -orient horizontal -resolution 1.0 \
        -variable "$top\::integer__hscale" 
    vTcl:DefineAlias "$site_4_0.integer__hscale" "Scale1" vTcl:WidgetProc "Toplevel1" 1
    entry $site_4_0.integer__entry \
        -background white -disabledforeground #a1a4a1 -insertbackground black \
        -textvariable "$top\::integer__entry" -width 6 
    vTcl:DefineAlias "$site_4_0.integer__entry" "Entry1" vTcl:WidgetProc "Toplevel1" 1
    pack $site_4_0.integer__spinbox \
        -in $site_4_0 -anchor s -expand 0 -fill none -padx 10 -side left 
    pack $site_4_0.integer__hscale \
        -in $site_4_0 -anchor center -expand 0 -fill none -padx 10 \
        -side right 
    pack $site_4_0.integer__entry \
        -in $site_4_0 -anchor s -expand 1 -fill none -padx 10 -side top 
    pack $site_3_0.label7 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side left 
    pack $site_3_0.integer__label \
        -in $site_3_0 -anchor center -expand 0 -fill none -side right 
    pack $site_3_0.frame_integer \
        -in $site_3_0 -anchor center -expand 0 -fill none -side top 
    frame $top.row5 \
        -borderwidth 2 -relief groove -height 75 -width 125 
    vTcl:DefineAlias "$top.row5" "Frame8" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.row5
    label $site_3_0.label8 \
        -disabledforeground #a1a4a1 -text float 
    vTcl:DefineAlias "$site_3_0.label8" "Label12" vTcl:WidgetProc "Toplevel1" 1
    label $site_3_0.float__label \
        -disabledforeground #a1a4a1 -text %.1f 
    vTcl:DefineAlias "$site_3_0.float__label" "Label13" vTcl:WidgetProc "Toplevel1" 1
    frame $site_3_0.frame_float \
        -borderwidth 2 -relief groove -height 75 -width 125 
    vTcl:DefineAlias "$site_3_0.frame_float" "Frame9" vTcl:WidgetProc "Toplevel1" 1
    set site_4_0 $site_3_0.frame_float
    spinbox $site_4_0.float__spinbox \
        -activebackground #f7fbf7 -disabledforeground #a1a4a1 \
        -foreground black -from 0.0 -highlightcolor black -increment 0.5 \
        -insertbackground black -selectbackground #c1c5c1 \
        -selectforeground black -to 100.0 -width 6 
    vTcl:DefineAlias "$site_4_0.float__spinbox" "Spinbox2" vTcl:WidgetProc "Toplevel1" 1
    scale $site_4_0.float__hscale \
        -bigincrement 0.0 -from 0.0 -orient horizontal -resolution 0.5 \
        -variable "$top\::float__hscale" 
    vTcl:DefineAlias "$site_4_0.float__hscale" "Scale2" vTcl:WidgetProc "Toplevel1" 1
    entry $site_4_0.float__entry \
        -background white -disabledforeground #a1a4a1 -insertbackground black \
        -textvariable "$top\::float__entry" -width 6 
    vTcl:DefineAlias "$site_4_0.float__entry" "Entry2" vTcl:WidgetProc "Toplevel1" 1
    pack $site_4_0.float__spinbox \
        -in $site_4_0 -anchor s -expand 0 -fill none -padx 10 -side left 
    pack $site_4_0.float__hscale \
        -in $site_4_0 -anchor center -expand 0 -fill none -padx 10 \
        -side right 
    pack $site_4_0.float__entry \
        -in $site_4_0 -anchor s -expand 1 -fill none -padx 10 -side top 
    pack $site_3_0.label8 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side left 
    pack $site_3_0.float__label \
        -in $site_3_0 -anchor center -expand 0 -fill none -side right 
    pack $site_3_0.frame_float \
        -in $site_3_0 -anchor center -expand 0 -fill none -side top 
    frame $top.row6 \
        -borderwidth 2 -relief groove -height 75 -width 125 
    vTcl:DefineAlias "$top.row6" "Frame10" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.row6
    label $site_3_0.label9 \
        -disabledforeground #a1a4a1 -text string 
    vTcl:DefineAlias "$site_3_0.label9" "Label14" vTcl:WidgetProc "Toplevel1" 1
    label $site_3_0.string__label \
        -disabledforeground #a1a4a1 -text string 
    vTcl:DefineAlias "$site_3_0.string__label" "Label15" vTcl:WidgetProc "Toplevel1" 1
    entry $site_3_0.string__entry \
        -background white -disabledforeground #a1a4a1 -insertbackground black \
        -textvariable "$top\::string__entry" 
    vTcl:DefineAlias "$site_3_0.string__entry" "Entry3" vTcl:WidgetProc "Toplevel1" 1
    pack $site_3_0.label9 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side left 
    pack $site_3_0.string__label \
        -in $site_3_0 -anchor center -expand 0 -fill none -side right 
    pack $site_3_0.string__entry \
        -in $site_3_0 -anchor center -expand 0 -fill none -side top 
    frame $top.row7 \
        -borderwidth 2 -relief groove -height 75 -width 125 
    vTcl:DefineAlias "$top.row7" "Frame11" vTcl:WidgetProc "Toplevel1" 1
    set site_3_0 $top.row7
    label $site_3_0.label10 \
        -disabledforeground #a1a4a1 -text string 
    vTcl:DefineAlias "$site_3_0.label10" "Label16" vTcl:WidgetProc "Toplevel1" 1
    label $site_3_0.textview__label \
        -disabledforeground #a1a4a1 -text string 
    vTcl:DefineAlias "$site_3_0.textview__label" "Label17" vTcl:WidgetProc "Toplevel1" 1
    text $site_3_0.textview__text \
        -background white -foreground black -height 4 -highlightcolor black \
        -insertbackground black -selectbackground #c1c5c1 \
        -selectforeground black -width 35 -wrap none 
    pack $site_3_0.label10 \
        -in $site_3_0 -anchor center -expand 0 -fill none -side left 
    pack $site_3_0.textview__label \
        -in $site_3_0 -anchor center -expand 0 -fill none -side right 
    pack $site_3_0.textview__text \
        -in $site_3_0 -anchor center -expand 0 -fill none -side top 
    ###################
    # SETTING GEOMETRY
    ###################
    pack $top.row0 \
        -in $top -anchor center -expand 1 -fill x -side top 
    pack $top.row1 \
        -in $top -anchor center -expand 1 -fill x -side top 
    pack $top.row2 \
        -in $top -anchor center -expand 1 -fill x -side top 
    pack $top.row3 \
        -in $top -anchor center -expand 1 -fill x -side top 
    pack $top.row4 \
        -in $top -anchor center -expand 1 -fill x -side top 
    pack $top.row5 \
        -in $top -anchor center -expand 1 -fill x -side top 
    pack $top.row6 \
        -in $top -anchor center -expand 1 -fill x -side top 
    pack $top.row7 \
        -in $top -anchor center -expand 1 -fill x -side top 

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
Window show .root

main $argc $argv
