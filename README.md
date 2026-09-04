# Sublime Text 2 Plugin: The Incrementor

A Sublime Text 2 Plugin that can generate a sequence of numbers using search and replace.

There is a Sublime Text 3 port available [here](https://github.com/born2c0de/Incrementor).

Example (Before):

    10. Bob
    12. Larse
    15. Billy

> Find: `[0-9]+\.`
> Replace: `\i.`

Example (After):

    1. Bob
    2. Larse
    3. Billy

You can also take start and step arguments `\i(start,step)` in parenthesis.

Example (Before):

    10. Bob
    12. Larse
    15. Billy

> Find: `[0-9]+\.`
> Replace: `\i(10,10).`

Example (After):

    10. Bob
    20. Larse
    30. Billy

Lastly, The Incrementor also supports negative steps! `\i(start,-step)`

Example (Before):

    10. Bob
    12. Larse
    15. Billy

> Find: `[0-9]+\.`
> Replace: `\i(100,-10).`

Example (After):

    100. Bob
    90. Larse
    80. Billy

## Using

Use the Command Palette (`Ctrl+Shift+P`) and search for `Incrementor: Generate a sequence of numbers` to prompt for your find and replace.


## Installation

### By Package Control

1. Download & Install **`Sublime Text 3`** (https://www.sublimetext.com/3)
1. Go to the menu **`Tools -> Install Package Control`**, then,
    wait few seconds until the installation finishes up
1. Now,
    Go to the menu **`Preferences -> Package Control`**
1. Type **`Add Channel`** on the opened quick panel and press <kbd>Enter</kbd>
1. Then,
    input the following address and press <kbd>Enter</kbd>
    ```
    https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json
    ```
1. Go to the menu **`Tools -> Command Palette...
    (Ctrl+Shift+P)`**
1. Type **`Preferences:
    Package Control Settings – User`** on the opened quick panel and press <kbd>Enter</kbd>
1. Then,
    find the following setting on your **`Package Control.sublime-settings`** file:
    ```js
    "channels":
    [
        "https://packagecontrol.io/channel_v3.json",
        "https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json",
    ],
    ```
1. And,
    change it to the following, i.e.,
    put the **`https://raw.githubusercontent...`** line as first:
    ```js
    "channels":
    [
        "https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json",
        "https://packagecontrol.io/channel_v3.json",
    ],
    ```
    * The **`https://raw.githubusercontent...`** line must to be added before the **`https://packagecontrol.io...`** one, otherwise,
      you will not install this forked version of the package,
      but the original available on the Package Control default channel **`https://packagecontrol.io...`**
    > [!WARNING]
    > Placing this custom channel before the default channel changes Package Control's resolution globally.
    > Packages from this channel with the same name will override versions from the default channel.
    >
    > You can review the channel contents here:
    > https://raw.githubusercontent.com/evandrocoan/StudioChannel/master/channel.json
1. Now,
    go to the menu **`Preferences -> Package Control`**
1. Type **`Install Package`** on the opened quick panel and press <kbd>Enter</kbd>
1. Then,
    search for **`Incrementor`** and press <kbd>Enter</kbd>

See also:

1. [ITE - Integrated Toolset Environment](https://github.com/evandrocoan/ITE)
1. [Package control docs](https://packagecontrol.io/docs/usage) for details.


## Todo

- Replace based on order of selection as well as their direction. (Difficult)
- Scroll to matching pattern like sublime's default find window. (Easy)
- Allow prepending 0s to the initial number. (001, 002, 003, 004, etc.) (Intermediate)
- Add number of replaced items in statusbar after completion. (Intermediate)

## Contributors

Don't forget to add yourself!

[eBook Architects](info@ebookarchitects.com), [Chris](cdcasey@gmail.com), [Toby](codenamekt@gmail.com), [AJ](anthony@ebookarchitects.com)

## License

[Creative Commons Attribution 2.0 Generic](http://creativecommons.org/licenses/by/2.0/)
