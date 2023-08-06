// global variable to store canvas data
canvasDataSnapshot = "";

//draw photo to canvas
function drawPhoto(context,image_src, callback) {
  var img = new Image();
  img.src = image_src;
  img.onload = function() {
    context.drawImage(img,0,91,img.width,img.height);
    if (typeof callback !== "undefined") {
      console.log(context);
      callback(context);
    }
  };
}

function saveImage() {
  var canvas = document.getElementById("canvas"),
  context = canvas.getContext("2d");
  var img = new Image();
  img.src = $('#preview img').data('cropbox').getDataURL("image/png");
  img.onload = function() {
    context.drawImage(img,0,91,img.width,img.height);
    canvasDataSnapshot = context.canvas.toDataURL("image/png");
   }
   console.log("image saved");
}

// Draw frame on top of image that is returned from postRawPhoto() success callback
// Drawn to canvas
function drawFrame(context, callback) {
  options = {
    name : $('#name').val(),
    frame_url: frame_url
  };

    //lay out the frame
    if (options.frame_url !== "undefined") {
      var frame = new Image();
      frame.src = options.frame_url;
      frame.onload = function() {
        var canvas = context.canvas;
        context.drawImage(frame,0,0,canvas.clientWidth,canvas.clientHeight);
        //lay out the name
        if (options.name !== "undefined") {
          context.fillStyle = "#FFF";
          context.font = "bold 32px House Slant";
          context.textAlign = "start";
          context.fillText(options.name, 140, 53);
        }

        if (typeof callback !== "undefined") {
          callback(context);
        }
      };
    }

}

var postRawPhoto = function(form, dropbox) {
  $.ajax({
    type: 'POST',
    url:"upload_raw_photo",
    contentType: false,
    processData: false,
    data: form,
    error: function(data) {
        alert('Please select a photo to upload before submitting.')
    },
    success: function(data) {
      var data = $.parseJSON(data);
      //clears canvas
      var canvas = document.getElementById("canvas");
      var context = canvas.getContext("2d");
      context.setTransform(1, 0, 0, 1, 0, 0);
      context.clearRect(0,0,canvas.width,canvas.height);
      current_image = new Image()
      current_image.src = 'data:image/png;base64, ' + data['resized_file']

      // no exif data is available from the returned image
      // so, use orientation info captured earlier
      console.log("Here I am again, later in the program");
      console.log(window.image_orientation);
      dropbox.appendChild(current_image);
      initCropper();
      context = document.getElementById("canvas").getContext("2d");
      drawFrame(context);
    }
  });
}



function postPhoto(context, access_token) {
  $('input').removeClass('error');
  $('label').removeClass('error');
  var base64img = context.canvas.toDataURL("image/png");
  $.ajax({
    type: 'POST',
    url: 'submit',
    contentType: false,
    data: {
      captioned_photo: base64img,
      name:$('#name').val(),
    },
    error: function(jqXHR, textStatus) {
      var errors = $.parseJSON(jqXHR.responseText);
      $('input#'+errors.field).addClass('error')
      .parent()
      .prepend("<p>" + errors.message + "</p>");
      $('label[for="'+errors.field+'"]').addClass('error');
      $("#share-to-facebook").removeAttr("disabled");
    },
    success: function(jqXHR, textStatus, errorThrown) {
      PostImageToFacebook(access_token);
      saveImage();
      $("#preview, #upload h2, #upload .field, #upload .social-buttons-container, .disclaimer").hide();        
      $("#thank-you").slideDown( 'slow' );   
    }
  });
}

//redraw when we add text and such
function redraw() {
  var canvas = document.getElementById("canvas"),
  context = canvas.getContext("2d");
  drawPhoto(context,$('#preview img').attr('src'), drawFrame);
}

// update the global canvasDataSnapshot variable
function updateCanvasDataSnapshot() {
    var canvas = document.getElementById("canvas");
    var imageData = canvas.toDataURL("image/png");
    canvasDataSnapshot = imageData;
    console.log("canvas snapshot updated");
}

function switchStep(current, next) {
  $('[data-step="' + current + '"]').hide();
  $('[data-step="' + next + '"]').show();
  stepTwoEvents();
}

function initCropper() {
  $('#preview img').cropbox({
    "width":390,
    "height":263
  });
}

function downloadCanvas(link, imgData, filename) {
  link.href = imgData;
  link.download = filename;
}

function imageUpload(dropbox) {
  var image_dimension_x = 390,
      image_dimension_y = 390,
      scaled_width = 0,
      scaled_height = 0,
      x1 = 0,
      y1 = 0,
      x2 = 0,
      y2 = 0,
      current_image = null,
      ias = null,
      file = $("#fileInput").get(0).files[0];

  loadImage.parseMetaData(file, function (data) {
    if (!data.imageHead) {
      console.log("no data in image head");
        return;
    }

    var orientation = data.exif.get('Orientation');
    console.log("Photo orientation code:");
    console.log(orientation);
    window.image_orientation = orientation;
  });
  
  var imageType = /image.*/;

  if (file.type.match(imageType)) {
    var reader = new FileReader();

    reader.onload = function(e) {
      var file = $("#fileInput").get(0).files[0];
      var rawPhotoForm = new FormData($('#rawPhoto')[0]);
      rawPhotoForm.append('photo', file);
      switchStep(1,2);  
      postRawPhoto(rawPhotoForm, dropbox);
    }
    reader.readAsDataURL(file);

  } else {
    $("#fileInput").get(0).html("File not supported!");
  }
}


$("#name").change(function() {
  var canvas = document.getElementById("canvas"),
  context = canvas.getContext("2d");
  drawFrame(context);
  // saveImage();

});

function charCountDown(inputEl, counterEl) {
      if(!inputEl || !counterEl){return false}; // catches errors
      var limit = inputEl.maxLength;
      var counter = counterEl;
      var remaining = limit - inputEl.value.length;
      counter.innerHTML = remaining+ " of " + limit + " remaining";
}

var stepOneEvents = function() {    
    $("#examplePhoto").click(function() {
      $('#fileInput').click();
    });

    $('#fileInput').change(function() {
      imageUpload($('#preview').get(0));
    });
}


var initModal = function(context) {
  base64img = new Image();
  base64img.src = context.canvas.toDataURL("image/png");
  base64img.onload = function(e) {
    $('#modal_image_preview').append(base64img);
  }

  $('#share-modal').modal({onOpen: function (dialog) {
    dialog.overlay.fadeIn('slow', function () {
      dialog.container.fadeIn('slow', function () {
        dialog.data.fadeIn('slow');  
      });  
    });
  }, overlayClose:true});
      
}


var stepTwoEvents = function() {    
 
 $("#previewShare").on('click', function(e) {
      e.preventDefault();
      var canvas = document.getElementById("canvas"),
          context = canvas.getContext("2d");
      drawPhoto(context, $('#preview img').data('cropbox').getDataURL('image/png'), initModal)
 });

 $("#share-to-facebook").on('click', function(e) {
    e.preventDefault();
    
    // Prevent more than one share at a time.
    this.disabled=true;

    // Get canvas context for drawing photo
    var canvas = document.getElementById("canvas"),
        context = canvas.getContext("2d");

    // TODO: Move to the modal
    FB.login(function(response) {
       // TODO: Maybe make a try/catch instead and provide a real error...
       if (response.authResponse) {
          var access_token =   FB.getAuthResponse()['accessToken'];
          drawPhoto(context,$('#preview img').data('cropbox').getDataURL("image/png"), postPhoto(context, access_token));
       } else {
          console.log("User cancelled login or did not fully authorize");
       }
    }, {scope: 'publish_actions'});
  });  

  // new download function binding directly to element
  $("#download").on('click', function(e) {
    link = this;
    link.href = canvasDataSnapshot;
    link.download = 'walmart-test.png';
  }, false);

  // character count
  $("#name").keypress( function() {
    var inputEl = document.getElementById("name");
    var counterEl = document.getElementById("charcount");
    charCountDown(inputEl, counterEl);
  });

  $('#saveme').click( function(e){
    e.preventDefault();
    saveImage();
  });

  $('#show-thankyou-box').click( function(e){
    e.preventDefault();
    saveImage();
    $("#preview, #upload h2, #upload .field, #upload .social-buttons-container, .disclaimer").hide();        
    $("#thank-you").slideDown( 'slow' );   
  });
  
}

$(document).ready(function() {
    // Make sure we cache our AJAX requests.
    $.ajaxSetup({ cache: true });    
    // Kick off Facebook app integration
    // TODO: Add Facebook app ID as a package setting.
    $.getScript('//connect.facebook.net/en_US/all.js', function(){
      FB.init({
        appId: '872566102800653',
      });     

      // Add event listeners for the first step of the app.
      stepOneEvents();
    });
});