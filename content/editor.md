# the editor behind this blog

<!-- date: 2026-10-22 -->

Most writing tools are built for people who can sit down and write for an hour. I can't. I write in short bursts, usually one paragraph at a time, and anything that puts a file tree, a toolbar, or a settings pane in front of me is enough to lose the thread.

So I built a small one. It's the thing I'm using to write this.

It's Rust, with Axum serving a single HTML page. No front-end build step, no framework. The binary is about two megabytes, and it writes straight into the markdown files that build this site, so there's no import or export step. Autosave is on by default; the only feedback is a dot in the corner that turns green when the file is on disk.

The design is mostly subtraction:

- one screen at a time: a list, or the editor, or a preview
- no menus, no labels, no word count — icons only, and they fade out while you type
- focus mode dims every block except the one your cursor is in, so the page around the sentence you're writing basically disappears
- it opens on the paragraph you're writing with empty space below, instead of dropping you at the top of a wall of text

The poetry part is where it stops behaving like a normal text editor.

Poems aren't paragraphs. In the [poetry section](poetry/) a blank line separates stanzas, line breaks inside a stanza are kept exactly as typed, and focus mode dims by stanza rather than by paragraph — so the whole stanza stays lit while the rest of the poem recedes. Indentation survives. Nothing reflows or rewraps into a wall.

One editor handles both collections. There's a two-icon switch in the corner: the blog on one side, poetry on the other. Same keys, same autosave, same focus mode; only the rendering changes.

It's local-first, which means it runs on my machine and edits my files directly. On a phone it installs to the home screen as an app, and the whole thing is small enough that it doesn't feel like software.

That's the whole idea: an editor that gets out of the way before the mood does.
