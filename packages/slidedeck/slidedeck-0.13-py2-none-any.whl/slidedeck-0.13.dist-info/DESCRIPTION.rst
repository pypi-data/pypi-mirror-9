This is a repackaging of the google io 2012 slidedeck,
to be a little easier to use and more suitable for scientific
presentations.

Example slides: http://cdn.rawgit.com/rmcgibbo/slidedeck-example/master/index.html

You edit and author your entire presentation in markdown. All the metadata
about your presentation is set within the markdown file, including things
like the title and author. You run `slidedeck create` to make a new deck.
This will create a new directory with your project. In particular, there will
be a fine in there called slides.md that contains the markdown source for
your slides. `slidedeck render` will render your deck from markdown to html5.
`slidedeck watch` will watch your project and rerender the slides whenever
you change the content (useful for iterative development).


