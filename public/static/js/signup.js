$( function() {
    $( "#slider-range" ).slider({
      range: true,
      min: 18,
      max: 85,
      values: [ 18, 35 ],
      slide: function( event, ui ) {
        $( "#age-amount" ).val( ui.values[0] + " - " + ui.values[1] );
      }
    });
    $( "#age-amount" ).val( $( "#slider-range" ).slider( "values", 0 ) +
      " - " + $( "#slider-range" ).slider( "values", 1 ) );
} );



