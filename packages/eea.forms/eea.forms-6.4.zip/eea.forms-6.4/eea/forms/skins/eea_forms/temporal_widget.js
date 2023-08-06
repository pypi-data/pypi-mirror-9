(function($){
  $(document).ready(function() {

    var field = $("#temporalCoverage");

    var numeric_keypad = [96, 97, 98, 99, 100, 101, 102, 103, 104, 105];
    var skip_keys = [8];

    var dynamic = $("#temporal_btn");
    dynamic.parent().css({"font-weight": "normal"});


    var old_value = "";


    function get_tokenInput_values(){
      var field_value = field.val();
      if(field_value){
        var value = field_value.split("\n");
        return $.map(value, function(val, idx){
          return {name: val, id: val};
        });
      }
    }

    function check_is_dynamic(elem){
      var tokenInput = $("ul.token-input-list-facebook");
      var field_value = field.val();
      if(elem.is(":checked")){
        tokenInput.hide();
        old_value = field_value !== "-1" ? field_value : "";
        field.val("-1");
      } else {
        tokenInput.show();
        if(old_value || field.val() === "-1"){
          field.tokenInput("clear");
          field.val(old_value);
          var token_values = get_tokenInput_values();
          if(token_values){
            $.each(token_values, function(i, o){
              field.tokenInput("add", o);
            });
          }
        }
      }
    }

    dynamic.on("change", function(evt){
      check_is_dynamic($(this));
    });


    field.tokenInput([], {
      theme: "facebook",
      tokenValue: "name",
      hintText: "Type in a year or a range of years (e.g. 1999-2005).",
      searchingText: "",
      noResultsText: "",
      tokenDelimiter: "\n",
      onReady: function(){
        check_is_dynamic(dynamic);
      },
      onAdd: function(item) {
          var context = field[0];
          var current_tags = context.value.split('\n');
          var new_tag_name = item.name;
          if (current_tags.indexOf(new_tag_name) === -1) {
              context.value += "\n" + new_tag_name;
          }
      },
      onDelete: function(item) {
          var context = field[0];
          var tokens = context.value.split('\n');
          var item_name = item.name;
          var i, length, token, output = [];
          for (i = 0, length = tokens.length; i < length; i += 1) {
              token = tokens[i];
              if (token !== item_name) {
                output.push(token);
              }
          }
        context.value = output.join('\n');
      },
      prePopulate: get_tokenInput_values(),
      allowNewTokens: true
    });

    function check_isNaN(value, keycode){
      if(numeric_keypad.indexOf(keycode) != -1){
        return false;
      }
      if(value === " "){
        return true;
      } else {
        return isNaN(value);
      }
    }

    $("#token-input-temporalCoverage").on("keydown", function(evt){
      var pressed = String.fromCharCode(evt.keyCode);
      var field_value = evt.srcElement.value.trim();


      if(skip_keys.indexOf(evt.keyCode) === -1){
        if(field_value.length === 4){
          if(check_isNaN(pressed, evt.keyCode)){
            return false;
          } else {
            evt.srcElement.value = field_value + "-";
          }
        }
        else if(check_isNaN(pressed, evt.keyCode)) {
          return false;
        }

        if(field_value.length === 9){
          return false;
        }
      }
    });

  });
})(jQuery);
