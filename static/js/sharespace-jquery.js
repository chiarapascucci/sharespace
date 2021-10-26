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

    $("#main_category").change(function(){
		const url = $("#add_item_form").attr("data-sub-cat-url");
		const catID = $(this).val();

		$.ajax({
			url : url,
			data: { 'main_category_id' : catID },
			success : function(data) {
				$("#sec_category").html(data);
			}
		});
	});

	$("#postcode").load(lookup_func())



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

function populate_address(){
    const sel_adr = document.getElementById("address_list");
    console.log(sel_adr.selectedIndex)
    var str_address = sel_adr.options[sel_adr.selectedIndex].text
    console.log(str_address)
    tokens = str_address.split(',')
    console.log(tokens.length);
    document.getElementById("id_adr_line_1").value = tokens[0];
    document.getElementById("id_adr_line_2").value = tokens[1];
    document.getElementById("id_adr_line_3").value = tokens[2];
    document.getElementById("id_adr_line_4").value = tokens[3];
    document.getElementById("id_locality").value = tokens[4];
    document.getElementById("id_city").value = tokens[5];
    document.getElementById("id_county").value = tokens[6];

}
