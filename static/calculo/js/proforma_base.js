$(document).ready(function(){
    $("div.divform > input").addClass("form-control")

    $( "#button0" ).click(function() {
	$( "#div0" ).show( "slow" );
    });
    $( "#button0h" ).click(function() {
	$( "#div0" ).hide( "slow" );
    });
    $( "#button1" ).click(function() {
	$( "#div1" ).show( "slow" );
    });
    $( "#button2" ).click(function() {
	$( "#div2" ).show( "slow" );
    });
    $( "#button3" ).click(function() {
	$(".div3").show( "slow" );
	$(this).hide("slow");
    });
    $( "#button3h" ).click(function() {
	$(".div3" ).hide( "slow" );
	$("#button3" ).show( "slow" );
    });

});
