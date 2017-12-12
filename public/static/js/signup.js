$( function() {

    $( "#slider-range" ).slider({
      range: true,
      min: 18,
      max: 85,
      classes: {
        "ui-slider-handle": "round"
      },
      values: [ 18, 35 ],
      slide: function( event, ui ) {
        $( "#age-amount" ).val( ui.values[0] + " - " + ui.values[1] );
      }
    });
    $( "#age-amount" ).val( $( "#slider-range" ).slider( "values", 0 ) +
      " - " + $( "#slider-range" ).slider( "values", 1 ) );

    var survey = []; //Bidimensional array: [ [1,3], [2,4] ]

    //Switcher function:
    $(".rb-tab").click(function(){
      //Spot switcher:
      $(this).parent().find(".rb-tab").removeClass("rb-tab-active");
      $(this).addClass("rb-tab-active");
    });
} );



