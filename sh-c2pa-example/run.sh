#!/bin/bash

filename="$1"

get_metadata() {
    c2patool "$1" | jq
}
get_metadata "$filename" | jq -r '.manifests | to_entries[0].value.assertions[0].data.actions[0].digitalSourceType'