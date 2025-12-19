Assist in composing software definition for a piece of software, code name "Sunnerrise". The overview and expected details of implementation/delivery follow.

The goal is to  build software assistant in keeping track of, performing categorizing, generation, creating promotion and publication related documents and media files for Suno-generated auto tracks.

Language of implementation: Python.

Structure: modular, different functions should be implemented as Python package that can be used also as command line tools.

Web interface required, with modules list in the sidebar; perhaps using Flask Python module.  Color choice: light-gray background, no too "acid" colors.

Database type proposed: MySQL. The database interface part should be implemented as a plugin, for possible switch to another DB engine.

When inventing modules identifiers (for publishing them as separate Python packages), use "sonnerrise-" prefix, i.e. "sonnerise-track-definitions"

The whole suite/piece of software should use the same YAML configuration, where the module takes its data and can use global ones (such as DB access credentials).

== Module 1. Suno Definitions list/editor. Should allow entering the below fields:

Title: freeform text up to 120 characters, should not be empty.

Annotation: freeform text up to 200 characters

Service to use: Dropdown, currently with single entry "Suno"

Model in use: multiple choice selector, listing at least "v3.5", "v4.0", "v4.5+", "v5.0"

Style of Music: text input, up to 1000 characters; add "Older models" checkbox to limit it to 200 characters. Checkbox should not be checked by default.

Lyrics: up to 3000 characters long. Either "Lyrics" or "Style of Music" should be entered, or both.

Persona: reference to a Persona (see Module 2); also a selector - use it as Voice or Style type of Persona. None by default.

Vocals override: dropdown: "Any", "Female", "Male".

Weights: "Audio influence" slider (0-100, default 25); "Style influence" slider (0-100, default 50); "Weirdness" slideer (0-100, default 50)

Cover of: Track reference (see Module 3), none by default.

Links: none of more links (URLs), none by default

Comments: freeform text field up to 32kb in length

Tracks: clickable list of tracks generated with this definition (add control to select one or more tracks, filtering by substring in their titles)

Web interface should allow 
- listing the definitions in paginated form (showing title, service, model and start of 'Style of Music', say 30 characters snippet)
- filtering by any mentioned fields (by substring in text freeform fields, by selected value in others)
- adding new/editing existing definition

== Module 2: Suno Personas definition list/editor. Should allow entering the below fields:

Name: freeform text up to 48 characters long

Style of Music: up to 1000 characters, optional.

Parental track: reference to a Track (Module 3 below), none by default

Comments: freeform text field up to 32kb in length

Web interface should allow 
- listing the Personas in paginated form (showing names)
- filtering by a substring in name
- adding new/editing existing Personas

== Module 3: Tracks definitions list/editor. Should allow entering the below fields:

Title: Track title, freeform text field up to 120 characters. Should be filled.

Album / Playlist: freeform text field up to 120 characters. Optional.

Definition reference: See Module 1. Link to a Definition (select by Title with substring filtering). Optional.

Links:  none of more links (URLs), none by default

Comments: freeform text field up to 32kb in length

Cover Art: external image URL; when displayed scaled to the biggest dimension to 256 pixels. Optional.

Lyrics: freeform text field up to 32kb in length

Events: date / time entries (date/time picking interface), freeform description (say, "Puiblish to Distrokid", "Mention at Instagram" etc). CAn be disabled (still displayed but are not mentioned in notifications).

== Module 4: Promotion. Should allow entering the below fields:

Track: the track (see Module 3). Mandatory.

Track Art definition: freeform text, text definition for AI generative still art (images) for the track, up to 32kb.

Track Canvas definition: freeform text, text definition for AI generative short video (canvas) for the track, up to 32kb.

Pitch:  freeform text - pitch/blurb/promo text snippets; up to 32kb.

Links: promotion/media links (URLs) with titles/descriptions (up to 120 character long description).

== Module 5: Calendar

Calendar display (weekly, monthly displays, with list of upcoming events displayed below, with notification of when it will happen/happened

Events should be clickable, allowing to either toggle disabled state, or navigate to the Track definition (Module 3) referring to the event.

== Module 6. Tools

Should allow exporting (downloading) current DB state or importing (loading) an existing DB dump. If DB version differs, create missing tables/related entities.

== Delivery

The output (in the repository) should include the Python packages definitions for the modules (in separate subdirectories), Docker compose file to deploy and run "Sunnerrise".
