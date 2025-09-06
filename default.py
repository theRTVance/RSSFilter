#!/usr/bin/env python3

import requests
import os
import feedparser # Used for parsing RSS/Atom feeds
import xml.etree.ElementTree as ET # Used for creating and manipulating XML structures
from xml.dom import minidom # Used for pretty-printing XML output
import re # Used for regular expressions
import requests
import xml.etree.ElementTree as ET
import os
import sys


# ==================== CONFIGURATION ====================
# The URL of the original podcast RSS feed you want to filter.
ORIGINAL_RSS_FEED_URL = "YOUR FEED HERE"

# The path where the new, filtered RSS feed XML file will be saved.
OUTPUT_RSS_FILE_PATH = "YOUR PATH HERE"

# A list of keywords (strings) that, if found in an episode's title, will cause
# that episode to be filtered out (removed) from the new RSS feed.
# The comparison is case-insensitive.
KEYWORDS_TO_FILTER = [
    #"Words ",
    #"To",
    #"Filter",
]

# A list of keywords (strings) that, if this list is NOT empty, an episode's title
# MUST contain at least one of these keywords to be included in the new RSS feed.
# If this list is empty, this "keep" filter is not applied.
# The comparison is case-insensitive.
KEYWORDS_TO_KEEP = [
    #"Words ",
    #"To",
    #"Keep",
]

# Keywords for filtering episode descriptions
DESCRIPTION_KEYWORDS_TO_FILTER = [
    #"Words ",
    #"To",
    #"Filter",
]
DESCRIPTION_KEYWORDS_TO_KEEP = [
    #"Words ",
    #"To",
    #"Keep",

]
# =======================================================


def filter_podcast_feed():
    """
    Downloads, filters, and saves a podcast RSS feed based on a set of rules.

    This function downloads an XML podcast feed, parses it, and removes any
    <item> elements (episodes) that do not match the criteria defined in the
    configuration section. The filtered feed is then saved to a new file.
    """
    print("Starting the podcast feed filtering process...")

    # Step 1: Download the XML content
    try:
        print(f"Downloading feed from: {ORIGINAL_RSS_FEED_URL}...")
        response = requests.get(ORIGINAL_RSS_FEED_URL, stream=True)
        response.raise_for_status()
        
        # Save to a temporary file to handle large feeds efficiently.
        temp_file_name = f"{os.path.basename(OUTPUT_RSS_FILE_PATH)}.temp"
        with open(temp_file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download successful.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the feed: {e}", file=sys.stderr)
        return

    # Step 2: Parse the XML file
    try:
        print("Parsing the XML content...")
        tree = ET.parse(temp_file_name)
        root = tree.getroot()
        print("XML parsing complete.")

    except ET.ParseError as e:
        print(f"Error parsing the XML file: {e}. The file might be malformed.", file=sys.stderr)
        os.remove(temp_file_name)
        return

    # Step 3: Filter the podcast episodes based on the configuration
    print("Filtering episodes...")
    channel = root.find("channel")

    if channel is None:
        print("Error: Could not find the <channel> element. This is not a valid RSS feed.", file=sys.stderr)
        os.remove(temp_file_name)
        return

    items_to_remove = []
    
    for item in channel.findall("item"):
        title_text = ""
        description_text = ""
        
        title_element = item.find("title")
        if title_element is not None and title_element.text:
            title_text = title_element.text.lower()
        
        description_element = item.find("description")
        if description_element is not None and description_element.text:
            description_text = description_element.text.lower()

        # The core filtering logic
        remove_episode = False
        
        # Check for keywords to filter (remove)
        if any(keyword.lower() in title_text for keyword in KEYWORDS_TO_FILTER):
            remove_episode = True
        
        if not remove_episode and any(keyword.lower() in description_text for keyword in DESCRIPTION_KEYWORDS_TO_FILTER):
            remove_episode = True
            
        # Check for keywords to keep (if the list is not empty)
        if not remove_episode and KEYWORDS_TO_KEEP:
            keep_episode = False
            if any(keyword.lower() in title_text for keyword in KEYWORDS_TO_KEEP):
                keep_episode = True
            if not keep_episode and any(keyword.lower() in description_text for keyword in DESCRIPTION_KEYWORDS_TO_KEEP):
                keep_episode = True
            
            if not keep_episode:
                remove_episode = True
        
        if remove_episode:
            items_to_remove.append(item)
    
    for item in items_to_remove:
        channel.remove(item)
        
    print(f"Filtering complete. Removed {len(items_to_remove)} episodes.")

    # Step 4: Write the filtered XML to a new file
    try:
        print(f"Saving the filtered feed to {OUTPUT_RSS_FILE_PATH}...")
        tree.write(OUTPUT_RSS_FILE_PATH, encoding="utf-8", xml_declaration=True)
        print("File saved successfully.")

    except IOError as e:
        print(f"Error writing the file: {e}", file=sys.stderr)

    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
            
    print("Process finished.")


if __name__ == "__main__":
    filter_podcast_feed()
