#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Incrementor for Sublime Text 3
Created on 25-Sep-2014 by Sanchit Karve
A Sublime Text 3 Plugin that can generate a sequence of numbers and letters using search and replace.

Ported to ST3 from Incrementor for ST2 created on 10-Jul-2012 by eBookArchitects
https://github.com/eBookArchitects/Incrementor

@copy: [Creative Commons Attribution 2.0 Generic](http://creativecommons.org/licenses/by/2.0/)
@python-ver: Python 2.6
"""
import sublime
import sublime_plugin
import re
from functools import partial
from types import GeneratorType


# I am saving the state in this class because it is a royal pain in the ass
# to keep typing `global` every time/everywhere I would like to use a global!
class State(object):
    ## While this is not 0, the input panel is open
    view_id = 0

    last_find_input = ""
    last_replace_input = ""


def restore_original_selection(view):
    selected_regions = view.get_regions( 'IncrementorBackup' )

    view.sel().clear()
    view.sel().add_all( selected_regions )

    view.erase_regions( 'IncrementorBackup' )
    view.erase_regions( 'IncrementorMarks' )


class IncrementorSelectionBackupRestoreCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        selected_regions = view.get_regions( 'IncrementorMarks' )

        view.sel().clear()
        view.sel().add_all( selected_regions )

        view.erase_regions( 'IncrementorBackup' )
        view.erase_regions( 'IncrementorMarks' )

        def delayed():
            view.run_command( 'soft_undo' )

        # https://github.com/SublimeTextIssues/Core/issues/2924
        sublime.set_timeout( delayed )


class IncrementorSelectionMarkRestoreCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        selected_regions = view.get_regions( 'IncrementorMarks' )

        view.sel().clear()
        view.sel().add_all( selected_regions )

        view.erase_regions( 'IncrementorMarks' )


class IncrementorReplaceHelperCommand(sublime_plugin.TextCommand):
    """"""
    def window(self):
        """"""
        return self.view.window()

    def match_gen(self, regex):
        """"""
        position = 0
        maximum_replacements = 100

        while True:
            region = self.view.find(regex, position)
            maximum_replacements -= 1

            if region and maximum_replacements > 0:
                yield region

                if region.size() > 2:
                    position = region.end() - 1
                else:
                    position = region.end()

            else:
                break

    def make_alpha_step(self, start='a', step=1, repeat_after='z'):
        """"""
        # optional repeat_after argument specifies the limit of the incrementation.
        # after the limit is reached, return to the start value and resume incrementing
        num = start
        while True:
            yield num
            # No validation here. Use carefully.
            num = chr(ord(num) + step)
            # return to start value if we're past repeat_after
            if repeat_after:
                if step < 0:
                    if num < repeat_after:
                        num = start
                else:
                    if num > repeat_after:
                        num = start

    def make_step(self, start=1, step=1, repeat_after=None):
        """"""
        # optional repeat_after argument specifies the limit of the incrementation.
        # after the limit is reached, return to the start value and resume incrementing
        num = start
        while True:
            yield num
            num = num + step
            if repeat_after:  # return to start value if we're past repeat_after
                if step < 0:
                    if num < repeat_after:
                        num = start
                else:
                    if num > repeat_after:
                        num = start

    def inc_replace(self, pattern_list, match):
        """"""
        try:
            replace_string = ''
            for i in range(len(pattern_list)):
                if isinstance(pattern_list[i], GeneratorType):
                    replace_string = replace_string + str(next(pattern_list[i]))
                else:
                    replace_string = replace_string + match.expand(pattern_list[i])
            return replace_string

        except Exception as error:
            status( "%s, %s, %s", error, pattern_list, replace_string )

    def parse_replace(self, replace):
        """"""
        replace_list = re.split(r'(\\[iaA]\(.+?\)|\\[iaA])', replace)
        replace_list[:] = [item for item in replace_list if item != '']
        for i in range(len(replace_list)):
            if replace_list[i] == '\\i':
                replace_list[i] = self.make_step()
            elif replace_list[i] == '\\a':
                replace_list[i] = self.make_alpha_step(start='a', repeat_after='z')
            elif replace_list[i] == '\\A':
                replace_list[i] = self.make_alpha_step(start='A', repeat_after='Z')
            elif re.match(r'^\\[i]\(.+?\)$', replace_list[i]):
                arg_list = [int(num) for num in re.split(r'\\i|\(|,| |\)', replace_list[i]) if num != '']
                if len(arg_list) == 3:
                    replace_list[i] = self.make_step(start=arg_list[0], step=arg_list[1], repeat_after=arg_list[2])
                elif len(arg_list) == 2:
                    replace_list[i] = self.make_step(start=arg_list[0], step=arg_list[1])
                else:
                    replace_list[i] = self.make_step(start=arg_list[0])

        return replace_list

    def run(self, edit, regex_to_find, replace_matches_with):
        """"""
        positiveMatch = []
        # print( "debug, 1 regex_to_find", regex_to_find, 'replace_matches_with', replace_matches_with )

        def regionSort(thisList):
            """"""

            # print( "debug, 2 thisList", thisList )
            for region in thisList:
                currentBegin = region.begin()

                # print( "debug, 3 currentBegin", currentBegin )
                currentEnd = region.end()

                # print( "debug, 4 currentEnd", currentEnd )
                if currentBegin > currentEnd:

                    region = sublime.Region(currentEnd, currentBegin)
                    # print( "debug, 5 region", region )

            # print( "debug, 6" )
            return sorted(thisList, key=lambda region: region.begin())

        startRegions = self.view.get_regions( 'IncrementorMarks' )

        # print( "debug, 7 startRegions", startRegions )
        startRegions = regionSort(startRegions)

        # print( "debug, 8" )
        view = self.view

        # print( "debug, 9" )
        reFind = re.compile(regex_to_find)

        # print( "debug, 10 reFind", reFind )
        myReplace = self.parse_replace(replace_matches_with)

        # print( "debug, 11 myReplace", myReplace )
        nEmptyRegions = []

        # print( "debug, 12" )
        if startRegions and replace_matches_with:
            # print( "debug, 13, Check if regions are in the given selections" )
            positiveMatch = []

            # print( "debug, 14, Create list of non-empty regions" )
            nEmptyRegions = [sRegion for sRegion in startRegions if not sRegion.empty()]


        # print( "debug, 15 startRegions", startRegions )
        # print( "debug, 16 If there is at least one empty region proceed to check in matches are in region" )
        if len(nEmptyRegions) == 0:

            # print( "debug, 17" )
            positiveMatch = self.match_gen(regex_to_find)

            for match in positiveMatch:

                # print( "debug, 18 match", match )
                myString = view.substr(match)

                # print( "debug, 19 myString", myString )
                newString = reFind.sub(partial(self.inc_replace, myReplace), myString)

                # print( "debug, 20 newString", newString )
                view.replace(edit, match, newString)
        else:

            # print( "debug, 21" )
            adjust = 0
            for sRegion in startRegions:

                # print( "debug, 22 sRegion", sRegion )
                matchRegions = self.match_gen(regex_to_find)

                # print( "debug, 23 adjust", adjust )
                if adjust:
                    # print( "debug, 24 matchRegions", matchRegions )
                    newBeg = sRegion.begin() + adjust

                    # print( "debug, 25 newBeg", newBeg )
                    newEnd = sRegion.end() + adjust

                    # print( "debug, 26 newEnd", newEnd )
                    sRegion = sublime.Region(newBeg, newEnd)

                    # print( "debug, 27 sRegion", sRegion )

                # print( "debug, 28" )
                for mRegion in matchRegions:

                    # print( "debug, 29" , mRegion)
                    if sRegion.contains(mRegion):

                        # print( "debug, 30" , sRegion)
                        myString = view.substr(mRegion)

                        # print( "debug, 31" , myString)
                        newString = reFind.sub(partial(self.inc_replace, myReplace), myString)

                        # print( "debug, 32" , newString)
                        view.erase(edit, mRegion)

                        # print( "debug, 33" )
                        charLen = view.insert(edit, mRegion.begin(), newString)

                        # print( "debug, 34" , charLen)
                        adjustment = charLen - mRegion.size()

                        # print( "debug, 35" )
                        adjust = adjust + adjustment

                        # print( "debug, 36" , adjust)
                        newEnd = sRegion.end() + adjustment

                        # print( "debug, 37" , newEnd)
                        sRegion = sublime.Region(sRegion.begin(), newEnd)

                        # print( "debug, 38" , sRegion)

        # print( "debug, 39 positiveMatch", positiveMatch )
        for match in positiveMatch:

            # print( "debug, 40 match", match )
            myString = view.substr(match)

            # print( "debug, 41 myString", myString )
            newString = reFind.sub(partial(self.inc_replace, myReplace), myString)

            # print( "debug, 42 newString", newString )
            view.replace(edit, match, newString)

        # print( "debug, 43" )


class IncrementorHighlightCommand(sublime_plugin.TextCommand):
    """Highlights regions or regular expression matches."""

    def run(self, edit, regex=None):
        view = self.view
        startRegions = view.get_regions( 'IncrementorBackup' )

        if startRegions and regex:
            matchRegions = view.find_all(regex)

            # Check if regions are in the given selections.
            positiveMatch = []

            # Create list of non-empty regions.
            nEmptyRegions = [sRegion for sRegion in startRegions if not sRegion.empty()]

            # If there is at least one empty region proceed to check in matches are in region.
            if len(nEmptyRegions) == 0:
                positiveMatch = matchRegions

            else:
                for mRegion in matchRegions:
                    for sRegion in startRegions:
                        if sRegion.contains(mRegion):
                            positiveMatch.append(mRegion)
            view.add_regions( 'IncrementorMarks', positiveMatch, 'comment', '', sublime.DRAW_OUTLINED )

        else:
            view.erase_regions( 'IncrementorMarks' )


class LivePreviewInputHandler(object):
    """ https://github.com/jbrooksuk/InsertNums/blob/master/InsertNums.py#L157 """
    def __init__(self, command, action):
        self.command = command
        self.action = action

    def start_preview_mode(self):
        view = self.view

        if State.view_id:
            self.revert_changes()

        else:
            State.view_id = view.id()

    def reset_preview_mode(self):
        if State.view_id:
            self.revert_changes()
            State.view_id = 0

    def revert_changes(self):
        """ Revert changes for clean undo history """
        last_command = self.view.command_history( 0 )

        if last_command[0].endswith( self.command ):
            self.view.run_command( self.action )


class IncrementorPromptPanelCommand(LivePreviewInputHandler, sublime_plugin.WindowCommand):
    def __init__(self, window):
        sublime_plugin.WindowCommand.__init__( self, window )

    def preview_find(self, text):

        if self.validate_find( text ):
            self.start_preview_mode()
            self.view.run_command( 'incrementor_highlight' )

    def on_cancel(self):
        self.reset_preview_mode()

    def show_find_panel(self):
        LivePreviewInputHandler.__init__( self, 'incrementor_highlight', 'soft_undo' )

        self.window.show_input_panel(
                'Find (w/ RegEx) :',
                '',
                on_done=self.find_callback_on_done,
                on_change=self.preview_find,
                on_cancel=self.on_cancel
            )

    def find_callback_on_done(self, find):
        self.reset_preview_mode()
        # ...
        self.show_replace_panel()

    def validate_find(self, text):

        if len( text ):
            try:
                return bool( re.compile( text ) )

            except Exception as error:
                status( "%s, %s", text, error )

    def show_replace_panel(self):
        LivePreviewInputHandler.__init__( self, 'incrementor_replace_helper', 'undo' )

        self.window.show_input_panel(
                'Replace (w/o RegEx) :',
                '',
                on_done=self.replace_callback_on_done,
                on_cancel=self.on_cancel,
                on_change=self.preview_replace
            )

    def replace_callback_on_done(self, text):
        self.reset_preview_mode()
        self.view.run_command( 'incrementor_replace_helper' )

    def preview_replace(self, text):

        if self.validate_replace( text ):
            self.start_preview_mode()
            self.view.run_command( 'incrementor_replace_helper' )

    def validate_replace(self, text):
        return len( text ) > 1

    def run(self):
        self.view = self.window.active_view()
        self.show_find_panel()


# class IncrementorSelectionSetupCommand(sublime_plugin.TextCommand):
#     def run(self, edit):
#         view = self.view

def selections_setup(view):
    view.erase_regions( 'IncrementorMarks' )

    selected_regions = []
    selections = view.sel()

    if selections:
        for selection in selections:
            region = sublime.Region(selection.end(), selection.begin())
            selected_regions.append(region)

        view.add_regions( 'IncrementorMarks', selected_regions )
        view.add_regions( 'IncrementorBackup', selected_regions )

        view.sel().clear()
        view.sel().add_all( selected_regions )
        view.run_command( 'incrementor_selection_setup_helper' )


class IncrementorSelectionSetupHelperCommand(sublime_plugin.TextCommand):
    """ https://github.com/SublimeTextIssues/Core/issues/2924 """
    def run(self, edit):
        view = self.view
        selections = view.sel()

        first_selection = selections[0]
        selections.clear()
        selections.add( sublime.Region( first_selection.begin(), first_selection.begin() ) )


class IncrementorPromptInputHandlerCommand(sublime_plugin.WindowCommand):

    def input(self, args):
        if "find_regex" not in args:
            view = self.window.active_view()
            return IncrementorFindRegexInputHandler( view )

        elif "replace_regex" not in args:
            return IncrementorReplaceInputHandler( self.window.active_view() )

        else:
            return None

    def run(self, find_regex, replace_regex):
        view = self.window.active_view()
        view.run_command( 'incrementor_replace_helper' )


class IncrementorFindRegexInputHandler(LivePreviewInputHandler, sublime_plugin.TextInputHandler):
    def __init__(self, view):
        LivePreviewInputHandler.__init__( self, 'incrementor_highlight', 'soft_undo' )
        self.view = view

    def name(self):
        return "find_regex"

    def placeholder(self):
        return "Find Regex"

    def cancel(self):
        self.reset_preview_mode()

    def initial_text(self):
        return ""

    def preview(self, text):

        if self.validate( text ):
            self.start_preview_mode()
            self.view.run_command( 'incrementor_highlight', { 'regex': text } )

    def confirm(self, text):
        self.reset_preview_mode()
        # ...
        self.view.run_command( 'incrementor_selection_mark_restore' )

    def validate(self, text):

        if len( text ):
            try:
                return bool( re.compile( text ) )

            except Exception as error:
                status( "%s, %s", text, error )

    def next_input(self, args):

        if "replace_regex" not in args:
            return IncrementorReplaceInputHandler( self.view )


class IncrementorReplaceInputHandler(LivePreviewInputHandler, sublime_plugin.TextInputHandler):
    def __init__(self, view):
        LivePreviewInputHandler.__init__( self, 'incrementor_replace_helper', 'undo' )
        self.view = view

    def name(self):
        return "replace_regex"

    def placeholder(self):
        return "Replace Regex"

    def initial_text(self):
        return ""

    def validate(self, text):
        return len( text ) > 1

    def preview(self, text):

        if self.validate( text ):
            self.start_preview_mode()
            self.view.run_command( 'incrementor_replace_helper' )

    def cancel(self):
        self.reset_preview_mode()

    def confirm(self, text):
        self.reset_preview_mode()

