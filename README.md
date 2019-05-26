[![Twitch](https://img.shields.io/badge/VizionzEvo-Twitch-blueviolet.svg)](https://twitch.tv/vizionzevo) [![Level Headed Gamers](https://img.shields.io/discord/371472684510609408.svg)](https://discord.gg/aY7vdnW) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Daily Stream Goals
Daily Stream Goals script for StreamLabs ChatBot. As a streamer, sometimes you stream multiple times in a day. As a streamer, you may also have daily goals you'd like to hit. For those that want the ability to keep track with an option to display your goals, this may be what you are looking for.

- Keep track of new followers, and subscritions. Bits and Donations to come!
- `.txt` output for goal and current counters.
- Add a separation string for formatted goal ouputs in their own `.txt` for you to display.
- Set your own reset timer in your local timezone. Maybe say, 5:00 AM for the late night streamers?

## Limitations
* Only available on Twitch platform.
* For the moment, client side only. Any events that occur while SLChatBot is off, will not be recorded. Thinking of a solution.

# Changes

## Pending
* Update `StreamlabsEventReceiver` to `v1.0.2`.

## v1.1.0
* Ability to set separation string between current current value and target goal.
* Output SubOutput.txt, FollowOutput.txt files `{current}{separator}{target}`
  *  Example: `10/500`

## v1.0.0
* Provide streamers a means of tracking and displaying daily goals for follows/subs/cheers/donations. Both 'current' and 'target' goals are written to .txt files for use to display on stream.

# Credits
* [Ocgineer](https://github.com/ocgineer) for his work on [Streamlabs Event Receiver](https://github.com/ocgineer/Streamlabs-Events-Receiver)! [Twitch](http://www.twitch.tv/ocgineer)

# Contributions
ALWAYS WELCOME!