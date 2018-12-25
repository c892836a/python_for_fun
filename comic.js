$(document).on("click", "img", function (event) {
	console.log(event)
    var imgClass = event.target.className;
    if (imgClass == "compressed") {
	    event.target.className = "original";
	    event.target.width = event.target.naturalWidth;
    }
    else if (imgClass == "original") {
	    event.target.className = "compressed";
	    event.target.width = "1200";
    }
});