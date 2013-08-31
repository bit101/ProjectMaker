( function( window, Modernizr ) {

	"use strict";

	Modernizr.load( [
		/*
		{
			test: Modernizr[testSomething],
			yep: filesToLoad
		},
		*/
		{
			load: ['lib/require.js'],
			callback: function( file ) {
				/* handler on async loaded file. */
			},
			complete: function() {

				define.amd.jQuery = true;
				require.config({
					baseUrl: '.',
					paths: {
						lib: './lib',
						script: './script',
						jquery: 'lib/jquery'
					}
				});

				require( ['jquery'], function( $ ) {
					$('<p>AppRequireJS template for STProjectMaker.</p>').appendTo( $("#placeholder") );
				});
			}
		}
	]);


})( this, Modernizr );