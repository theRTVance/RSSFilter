import feedparser # Used for parsing RSS/Atom feeds
import xml.etree.ElementTree as ET # Used for creating and manipulating XML structures
from xml.dom import minidom # Used for pretty-printing XML output
import requests # Used for making HTTP requests to fetch the RSS feed
import os # Used for interacting with the operating system, like file paths
from datetime import datetime # Used for handling dates and times, especially for RSS pubDate

# --- Configuration Section ---
# This is where you customize the script for your needs.

# The URL of the original podcast RSS feed you want to filter.
ORIGINAL_RSS_FEED_URL = "PLACE ORIGINAL RSS FEED HERE" # REPLACE WITH YOUR ACTUAL RSS FEED URL

# The path where the new, filtered RSS feed XML file will be saved.
# Make sure this path exists and the script has write permissions to it.
# Example for Windows: "C:\\Users\\YourUser\\Documents\\filtered_podcast.xml"
# Example for Linux/macOS: "/home/youruser/filtered_podcast.xml"
OUTPUT_RSS_FILE_PATH = "PUT YOUR PATH NAME HERE" # You can change this to a full path if needed

# A list of keywords (strings) that, if found in an episode's title, will cause
# that episode to be filtered out (removed) from the new RSS feed.
# The comparison is case-insensitive.
KEYWORDS_TO_FILTER = [
    #"unwanted topic",
    #"episode type to avoid",
    #"spoiler alert",
]

# A list of keywords (strings) that, if this list is NOT empty, an episode's title
# MUST contain at least one of these keywords to be included in the new RSS feed.
# If this list is empty, this "keep" filter is not applied.
# The comparison is case-insensitive.
KEYWORDS_TO_KEEP = [
    # "must-have keyword",
]

# A list of keywords (strings) that, if found in an episode's description, will cause
# that episode to be filtered out (removed) from the new RSS feed.
# The comparison is case-insensitive.
DESCRIPTION_KEYWORDS_TO_FILTER = [
    #"unwanted description term",
]

# A list of keywords (strings) that, if this list is NOT empty, an episode's description
# MUST contain at least one of these keywords to be included in the new RSS feed.
# If this list is empty, this "keep" filter is not applied.
# The comparison is case-insensitive.
DESCRIPTION_KEYWORDS_TO_KEEP = [
    #"required description term",
]

# --- End Configuration Section ---



def fetch_rss_feed(url):
    """
    Fetches the RSS feed content from the given URL.

    Args:
        url (str): The URL of the RSS feed.

    Returns:
        str: The content of the RSS feed as a string, or None if an error occurs.
    """
    print(f"Attempting to fetch RSS feed from: {url}")
    try:
        # Send an HTTP GET request to the URL.
        # timeout ensures the script doesn't hang indefinitely if the server is slow.
        response = requests.get(url, timeout=10)
        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()
        print("Successfully fetched RSS feed.")
        # Return the content of the response as text.
        return response.text
    except requests.exceptions.RequestException as e:
        # Catch any request-related errors (e.g., network issues, invalid URL, timeout)
        print(f"Error fetching RSS feed: {e}")
        return None

def filter_podcast_episodes(feed_content, keywords_to_filter, keywords_to_keep):
    """
    Parses the RSS feed content and filters episodes based on keywords in their titles and descriptions.
    It first applies 'inclusion' filters (if keywords_to_keep/description_keywords_to_keep are not empty),
    then 'exclusion' filters (keywords_to_filter/description_keywords_to_filter).

    Args:
        feed_content (str): The XML content of the RSS feed as a string.
        keywords_to_filter (list): A list of strings to exclude episode titles by.
        keywords_to_keep (list): A list of strings that episode titles must contain
                                  to be included (if this list is not empty).
    Returns:
        tuple: A tuple containing:
               - dict: The parsed feed object (from feedparser).
               - list: A list of filtered episode entries (dictionaries).
    """
    print("Parsing RSS feed and filtering episodes...")
    # Parse the RSS feed content using feedparser.
    # This converts the XML into a Python object structure that's easy to work with.
    feed = feedparser.parse(feed_content)

    # Check if the feed was parsed successfully.
    if not feed.entries:
        print("No entries found in the RSS feed or parsing failed.")
        return feed, []

    filtered_entries = []
    # Iterate through each episode (entry) in the parsed feed.
    for entry in feed.entries:
        # Get the title of the current episode. Default to empty string if not present.
        title = entry.get('title', '')
        # Convert the title to lowercase for case-insensitive comparison.
        title_lower = title.lower()

        # Get the description/summary of the current episode. Default to empty string if not present.
        # RSS feeds use 'summary' or 'description' for the main text content.
        description = entry.get('summary', entry.get('description', ''))
        description_lower = description.lower()

        # --- Step 1: Apply Title 'Keywords to Keep' filter (inclusion logic) ---
        passes_title_keep_filter = False
        if KEYWORDS_TO_KEEP: # Only apply this logic if there are keywords to keep
            for keep_keyword in KEYWORDS_TO_KEEP:
                if keep_keyword.lower() in title_lower:
                    passes_title_keep_filter = True
                    break
            if not passes_title_keep_filter:
                print(f"  Filtering out episode: '{title}' (title does not contain any required 'keep' keyword)")
                continue

        else: # If no 'keywords_to_keep' are specified, all episodes initially pass this title filter
            passes_title_keep_filter = True

        # --- Step 2: Apply Description 'Keywords to Keep' filter (inclusion logic) ---
        passes_description_keep_filter = False
        if DESCRIPTION_KEYWORDS_TO_KEEP: # Only apply this logic if there are description keywords to keep
            for keep_keyword in DESCRIPTION_KEYWORDS_TO_KEEP:
                if keep_keyword.lower() in description_lower:
                    passes_description_keep_filter = True
                    break
            if not passes_description_keep_filter:
                print(f"  Filtering out episode: '{title}' (description does not contain any required 'keep' keyword)")
                continue
        else: # If no 'description_keywords_to_keep' are specified, all episodes initially pass this description filter
            passes_description_keep_filter = True


        # --- Step 3: Apply Title 'Keywords to Filter' filter (exclusion logic) ---
        should_exclude_title = False
        for filter_keyword in KEYWORDS_TO_FILTER:
            if filter_keyword.lower() in title_lower:
                print(f"  Filtering out episode: '{title}' (title contains unwanted '{filter_keyword}')")
                should_exclude_title = True
                break
        if should_exclude_title:
            continue # Skip to the next entry if excluded by title filter

        # --- Step 4: Apply Description 'Keywords to Filter' filter (exclusion logic) ---
        should_exclude_description = False
        for filter_keyword in DESCRIPTION_KEYWORDS_TO_FILTER:
            if filter_keyword.lower() in description_lower:
                print(f"  Filtering out episode: '{title}' (description contains unwanted '{filter_keyword}')")
                should_exclude_description = True
                break
        if should_exclude_description:
            continue # Skip to the next entry if excluded by description filter

        # If the episode passed all 'keep' filters AND was not excluded by any 'filter' keywords, include it.
        filtered_entries.append(entry)
        # print(f"  Including episode: '{title}'") # Uncomment for verbose output

    print(f"Filtering complete. Original episodes: {len(feed.entries)}, Filtered episodes: {len(filtered_entries)}")
    return feed, filtered_entries

def generate_new_rss_xml(original_feed, filtered_entries):
    """
    Generates a new RSS 2.0 XML string from the original feed's metadata
    and the list of filtered entries. This version includes robust artwork handling.

    Args:
        original_feed (dict): The original parsed feed object (from feedparser)
                              containing channel metadata.
        filtered_entries (list): A list of filtered episode entries (dictionaries).

    Returns:
        str: The XML string of the new RSS feed.
    """
    print("Generating new RSS XML...")

    # Define a generic placeholder image URL if no artwork is found.
    # This URL points to a simple placeholder image service.
    GENERIC_PLACEHOLDER_IMAGE = "https://placehold.co/600x600/cccccc/333333?text=No+Artwork"

    # Create the root element for the RSS feed.
    # <rss version="2.0">
    rss = ET.Element("rss", version="2.0")

    # Create the channel element, which contains metadata about the podcast.
    # <channel>
    channel = ET.SubElement(rss, "channel")

    # Add essential channel elements from the original feed.
    # These are crucial for podcast clients to recognize the feed.
    # Use .get() with a default empty string to prevent errors if a field is missing.
    ET.SubElement(channel, "title").text = original_feed.feed.get('title', 'Filtered Podcast Feed')
    ET.SubElement(channel, "link").text = original_feed.feed.get('link', ORIGINAL_RSS_FEED_URL)
    ET.SubElement(channel, "description").text = original_feed.feed.get('description', 'A filtered podcast feed.')
    ET.SubElement(channel, "language").text = original_feed.feed.get('language', 'en-us')
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z") # Current time

    # Add iTunes specific tags for better podcast client compatibility.
    # These are often nested under a specific namespace.
    # Check if iTunes namespace exists in the original feed and use it, otherwise default.
    itunes_ns = '{http://www.itunes.com/dtds/podcast-1.0.dtd}'
    if 'itunes_namespace' in original_feed.namespaces:
        itunes_ns = '{' + original_feed.namespaces['itunes'] + '}'

    # Add iTunes specific channel elements
    ET.SubElement(channel, itunes_ns + "author").text = original_feed.feed.get('itunes_author', original_feed.feed.get('author', ''))
    ET.SubElement(channel, itunes_ns + "summary").text = original_feed.feed.get('itunes_summary', original_feed.feed.get('subtitle', ''))
    
    # Handle itunes:explicit for channel, ensuring string output
    channel_explicit = original_feed.feed.get('itunes_explicit', 'no')
    if isinstance(channel_explicit, bool):
        channel_explicit = 'yes' if channel_explicit else 'no'
    ET.SubElement(channel, itunes_ns + "explicit").text = channel_explicit

    # --- Artwork Handling for Channel (Podcast Overall) ---
    # Try to get the channel image from common feedparser locations.
    channel_image_url = None
    if 'image' in original_feed.feed and 'href' in original_feed.feed.image:
        channel_image_url = original_feed.feed.image.href
    elif 'itunes_image' in original_feed.feed and 'href' in original_feed.feed.itunes_image:
        channel_image_url = original_feed.feed.itunes_image.href
    
    # If no channel image found, use the generic placeholder.
    if not channel_image_url:
        channel_image_url = GENERIC_PLACEHOLDER_IMAGE

    # Add the iTunes image tag for the channel.
    itunes_channel_image = ET.SubElement(channel, itunes_ns + "image")
    itunes_channel_image.set('href', channel_image_url)


    # Add owner information (email and name)
    if 'itunes_owner' in original_feed.feed:
        itunes_owner = ET.SubElement(channel, itunes_ns + "owner")
        ET.SubElement(itunes_owner, itunes_ns + "name").text = original_feed.feed.itunes_owner.get('name', '')
        ET.SubElement(itunes_owner, itunes_ns + "email").text = original_feed.feed.itunes_owner.get('email', '')

    # Add categories (important for discoverability)
    if 'itunes_categories' in original_feed.feed:
        for category_data in original_feed.feed.itunes_categories:
            category = ET.SubElement(channel, itunes_ns + "category")
            category.set('text', category_data.get('term', ''))
            if 'subcategories' in category_data:
                for subcategory_data in category_data.subcategories:
                    subcategory = ET.SubElement(category, itunes_ns + "category")
                    subcategory.set('text', subcategory_data.get('term', ''))


    # Add each filtered episode as an <item> element.
    for entry in filtered_entries:
        item = ET.SubElement(channel, "item")

        # Add essential item elements.
        ET.SubElement(item, "title").text = entry.get('title', '')
        ET.SubElement(item, "description").text = entry.get('summary', entry.get('description', ''))
        ET.SubElement(item, "link").text = entry.get('link', '')

        # The 'guid' (Globally Unique Identifier) is crucial for podcast clients
        # to identify unique episodes and avoid re-downloading.
        # It should be a persistent, unique string for each episode.
        # If the original feed provides an 'id' or 'guid', use that.
        # Otherwise, fall back to the link or a combination of title and link.
        guid_text = entry.get('id', entry.get('guid', entry.get('link', entry.get('title', '') + entry.get('published', ''))))
        guid = ET.SubElement(item, "guid")
        guid.text = guid_text
        # isPermaLink="false" indicates that the GUID is not a URL.
        # If it *is* a URL and always points to the episode, you can set this to "true".
        guid.set('isPermaLink', 'false')

        # 'pubDate' is essential for podcast clients to order episodes and
        # determine when they were published.
        # feedparser usually provides 'published_parsed' as a time.struct_time.
        if 'published_parsed' in entry:
            # Convert the parsed time to a standard RSS date format.
            pub_date = datetime(*entry.published_parsed[:6]).strftime("%a, %d %b %Y %H:%M:%S %z")
            ET.SubElement(item, "pubDate").text = pub_date

        # The 'enclosure' tag is vital for podcast clients, as it points to the actual
        # audio file (MP3, M4A, etc.). It requires a URL, length (size in bytes), and type.
        if 'enclosures' in entry and entry.enclosures:
            enclosure = ET.SubElement(item, "enclosure")
            # Get the first enclosure (most podcasts have only one audio file per episode).
            first_enclosure = entry.enclosures[0]
            enclosure.set('url', first_enclosure.get('href', ''))
            enclosure.set('length', first_enclosure.get('length', '0'))
            enclosure.set('type', first_enclosure.get('type', 'audio/mpeg')) # Default to common audio type

        # Add iTunes specific item tags
        ET.SubElement(item, itunes_ns + "author").text = entry.get('itunes_author', entry.get('author', ''))
        ET.SubElement(item, itunes_ns + "summary").text = entry.get('itunes_summary', entry.get('summary', ''))
        ET.SubElement(item, itunes_ns + "duration").text = entry.get('itunes_duration', '')
        
        # Handle itunes:explicit for item, ensuring string output
        item_explicit = entry.get('itunes_explicit', 'no')
        if isinstance(item_explicit, bool):
            item_explicit = 'yes' if item_explicit else 'no'
        ET.SubElement(item, itunes_ns + "explicit").text = item_explicit
        
        # --- Artwork Handling for Individual Episode ---
        # Try to get the episode image from feedparser's itunes_image.
        episode_image_url = entry.get('itunes_image', {}).get('href')
        
        # If no episode-specific image, fall back to the channel image.
        # If channel image also not found, use the generic placeholder.
        if not episode_image_url:
            episode_image_url = channel_image_url # Use the channel image URL we determined earlier

        # Add the iTunes image tag for the item.
        itunes_item_image = ET.SubElement(item, itunes_ns + "image")
        itunes_item_image.set('href', episode_image_url)


    # Convert the ElementTree object to a string first
    raw_xml_string = ET.tostring(rss, encoding="utf-8", xml_declaration=True).decode('utf-8')

    # Use minidom to parse the raw XML string and then pretty-print it
    # This adds indentation and newlines for better human readability
    dom = minidom.parseString(raw_xml_string)
    xml_string = dom.toprettyxml(indent="  ", encoding="utf-8").decode('utf-8')

    print("New RSS XML generated.")
    return xml_string

def save_rss_to_file(xml_string, file_path):
    """
    Saves the generated RSS XML string to a specified file.

    Args:
        xml_string (str): The XML content to save.
        file_path (str): The path to the file where the XML will be saved.
    """
    print(f"Saving RSS feed to: {file_path}")
    try:
        # Open the file in write mode ('w') with UTF-8 encoding.
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        print("RSS feed saved successfully.")
    except IOError as e:
        # Catch any file-related errors (e.g., permissions, invalid path)
        print(f"Error saving RSS feed to file: {e}")

def main():
    """
    Main function to orchestrate the RSS filtering process.
    """
    print("Starting podcast RSS filter script...")

    # Step 1: Fetch the original RSS feed.
    rss_content = fetch_rss_feed(ORIGINAL_RSS_FEED_URL)
    if not rss_content:
        print("Failed to retrieve RSS feed. Exiting.")
        return # Exit if fetching failed.

    # Step 2: Filter the episodes based on keywords.
    # Now passing both keywords_to_filter and keywords_to_keep
    original_feed_parsed, filtered_entries = filter_podcast_episodes(rss_content, KEYWORDS_TO_FILTER, KEYWORDS_TO_KEEP)
    # original_feed_parsed contains the full parsed feed, including channel info.

    # Step 3: Generate the new RSS XML string.
    # We pass the original_feed_parsed to retain the channel metadata.
    new_rss_xml = generate_new_rss_xml(original_feed_parsed, filtered_entries)

    # Step 4: Save the new RSS XML to a file.
    save_rss_to_file(new_rss_xml, OUTPUT_RSS_FILE_PATH)

    print("Podcast RSS filter script finished.")

if __name__ == "__main__":
    # This ensures that main() is called only when the script is executed directly,
    # not when it's imported as a module into another script.
    main()
