# Silvius

Silvius is an open source system for controlling Linux by voice.

## Quick start instructions

- Try `./run.sh -t` to test speech recognition (it will ask which mic to use).
- Use `./run.sh -e` to execute results on your local machine.
- If you are getting spurious recognitions, try `./run.sh -G` to see the level of sound that forms background noise, and filter it out with `./run.sh -e -g 100`.

## Detailed Setup Instructions

Please go here for detailed setup instructions: http://voxhub.io/silvius

## Where is the Server?

As of this writing, a freely accessible server runs on
`silvius-server.voxhub.io` port `8019`. The code is available here:
https://github.com/dwks/silvius-backend

## Learn More

If you want to learn more, please join our mailing list:
https://groups.google.com/forum/#!forum/silvius

## About

Created by David Williams-King with Professor Homayoon Beigi at Columbia University. 

Send comments to `dwk at voxhub dot io`.
