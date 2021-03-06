$(document).ready(function() {

    /*
     * PrettyPrint plugin.
     *
     */
    // Init
    prettyPrint();

    // Prevent invalid links from jumping page scroll
    $('a[href=#]').click(function() {
        return false;
    });


    /* Belen's additions */

	// turn Edit columns dropdown into a multiselect menu
	$('.dropdown-menu input, .dropdown-menu label').click(function(e) {
		e.stopPropagation();
	});

    // enable popovers in any table cells that contain an anchor with the
    // .btn class applied, and make sure popovers work on click, are mutually
	// exclusive and they close when your click outside their area

	$('html').click(function(e){
		$('td > a.btn').popover('hide');
	});

	$('td > a.btn').popover({
		html:true,
		placement:'left',
		container:'body',
		trigger:'manual'
	}).click(function(e){
		$('td > a.btn').not(this).popover('hide');
		// ideally we would use 'toggle' here
		// but it seems buggy in our Bootstrap version
		$(this).popover('show');
		e.stopPropagation();
	});

	// enable tooltips for applied filters
	$('th a.btn-primary').tooltip({container:'body', html:true, placement:'bottom', delay:{hide:1500}});

	// enable help information tooltip
    $(".get-help").tooltip({container:'body', html:true, delay:{show:300}});

	// show help bubble only on hover inside tables
	$(".hover-help").css("visibility","hidden");
	$("th, td").hover(function () {
		$(this).find(".hover-help").css("visibility","visible");
	});
	$("th, td").mouseleave(function () {
		$(this).find(".hover-help").css("visibility","hidden");
	});

    // show task type and outcome in task details pages
    $(".task-info").tooltip({ container: 'body', html: true, delay: {show: 200}, placement: 'right' });

	// linking directly to tabs
	$(function(){
  		var hash = window.location.hash;
  		hash && $('ul.nav a[href="' + hash + '"]').tab('show');

  		$('.nav-tabs a').click(function (e) {
    		$(this).tab('show');
			$('body').scrollTop();
  		});
	});

});
