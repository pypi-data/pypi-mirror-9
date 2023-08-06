# scratch-ext
Access external locations (eg: GPIO) from scratch on the Raspberry Pi

# Running
Clone the repo (or download the .tar.gz). Move the .desktop file to your desktop, and start from there, or run from a terminal inside X:

```
bash ./startup.sh
```

# Usage
For now you can use the standard GPIO pins, broadcast a message in Scratch, saying `pin 11 on` will turn pin 11 high, `pin 11 off` will turn it low. You can also use `pin 11 1`, `pin 11 high`, etc. `gpio` is an alias for the ping command (eg `gpio 11 on`).

The script will update any changes in the gpio pins to the standard Scratch sensors. Open the 'sensing' tab, and select the pin you want to read from the list. This will return a 1 when high, and a 0 when low.

# Writing plugins
Add a .py file to the plugins dir, extend from plugin base, and implement the receive method, see the ExamplePlugin for an example.