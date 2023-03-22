var table = $('.table-container'); //add an id if necessary
var cols = $('.table-heading', table); //headers
var div = $('<div>'); //new div for checkboxes
cols.each(function(ind){	
	$('<label>').text($(this).text()).append(
		$('<input type="checkbox" checked=true>') //create new checkbox
	  .change(function(){
		  $('tr *:nth-child(' + (ind + 1) + ')', table).toggle();      	
	  })
	 ).appendTo(div);
});

table.before(div); //insert the new div before the table