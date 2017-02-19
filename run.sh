#!/bin/bash

if [[ $1 == '' || $1 == '-h' || $1 == '--help' ]]; then
    echo "usage: $0 -h | --help | -e | --execute | -t | --test | -d | --delete"
    echo -e "\t-h|--help: prints this help message"
    echo -e "\t-e|--execute: executes results of speech recognition"
    echo -e "\t-t|--test: prints results of speech recognition"
    echo -e "\t-d|--delete: deletes saved microphone selection"
    exit 0
fi

if [[ $1 != '-d' && $1 != '--delete' && $1 != '-t' && $1 != '--test' && $1 != '-e' && $1 != '--execute' ]]; then
    echo "Unknown command '$1'. Run with --help to see usage."
    exit 1
fi

if [[ $1 == '-d' || $1 == '--delete' ]]; then
    rm -f .selected-mic
    exit 0
fi

if [[ -f .selected-mic ]]; then
    which=$(cat .selected-mic)
else
    echo "No microphone selected..."
    echo "Finding microphones . . ."
    python stream/list-mics.py 2>/dev/null

    echo "Use which device?"
    read which
    echo $which >> .selected-mic
fi

echo "Selected microphone $which."

if [[ $1 == '-e' || $1 == '--execute' ]]; then
    python stream/mic.py -s silvius-server.voxhub.io -d $which | python grammar/main.py
elif [[ $1 == '-t' || $1 == '--test' ]]; then
    python stream/mic.py -s silvius-server.voxhub.io -d $which
fi
