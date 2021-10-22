$(document).ready(function() {
    console.log("page ready")

    $('p').hover(
        function() {
            $(this).css('color', 'red');
        },
        function() {
            $(this).css('color', 'black');
        }
    );
});


function lookup_func() {
			console.log("function exec");
			var url = "https://api.getAddress.io/find/";
			var api_key = "IdUvLkdSBki8uOcIoH01EQ33123";
			var post_code = document.getElementById("postcode").value;
			var f_post_code = post_code.toLowerCase().replace(' ', '');
			console.log(f_post_code);
			var full_url = url + f_post_code + "?api-key=" + api_key;
			console.log("full url " + full_url)
			var request = new XMLHttpRequest();
			request.onreadystatechange = function(){
			    if(this.readyState == 4 && this.status == 200){
				    var myData = JSON.parse(this.responseText);
				    console.log("here is the data retrieved");
				    console.log(myData);
				    populate_list(myData);
				    var selected_address = document.getElementById("address_list");
				    var str_address = selected_address.options[selected_address.selectedIndex].text;
				    populate_address(str_address);
			    }
			    else { console.log("error at request point" + request.status);
			    }
			};
			request.open("GET", full_url);
			request.send();
}

function populate_list(data) {
    const address_list = data['addresses'];
    var selection = document.getElementById("address_list");
    for (let i = 0; i< address_list.length; i++){
        var option = document.createElement("option");
        option.text = address_list[i];
        selection.add(option);
    }
}

function populate_address(address_str){
    const tokens = address_str.split(",");
    console.log(tokens.length);
    document.getElementById("adr_line_1").value = tokens[0];
    document.getElementById("adr_line_2").value = tokens[1];
    document.getElementById("adr_line_3").value = tokens[2];
    document.getElementById("adr_line_4").value = tokens[3];
    document.getElementById("locality").value = tokens[4];
    document.getElementById("city").value = tokens[5];
    document.getElementById("county").value = tokens[6];

}
