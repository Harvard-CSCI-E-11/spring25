"use strict";
/* jshint esversion: 8 */
const UPLOAD_TIMEOUT_SECONDS = 20;

////////////////////////////////////////////////////////////////
/// Enable the image-file upload when a file is selected and both the api-key and api-secret-key are provided.
function enable_disable_upload_button()
{
    const image_file =
    const enable = $('#image-file').val().length > 0 &&
          $('#api-key').val().length > 0 &&
          $('#api-secret-key').val().length > 0;
    $('#upload-button').prop('disabled', !enable);
    if (enable) {
        $('#message').html('ready to upload!');
    } else {
        $('#message').html(''); // clear the message if button is disabled
    }
}

/*
 *
 * Uploads a image using a presigned post. See:
 * https://aws.amazon.com/blogs/compute/uploading-to-amazon-s3-directly-from-a-web-or-mobile-application/
 * https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
 *
 * Presigned post is provided by the /api/new-image call (see below)
 */
async function upload_image_post(imageFile)
{
    // Get a presigned post from the server
    $('#message').html(`Requesting signed upload...`);
    let formData = new FormData();
    formData.append("api_key",              $('#api-key'));
    formData.append("api_secret_key",       $('#api-secret-key'));
    formData.append("image_data_length",  imageFile.fileSize);
    const r = await fetch(`${API_BASE}api/new-image`, { method:"POST", body:formData});
    const obj = await r.json();
    console.log('new-image obj=',obj);
    if (obj.error){
        $('#message').html(`Error getting upload URL: ${obj.message}`);
        return;
    }
    const image_id = window.image_id = obj.image_id;
    $('#message').html(`Uploading image ${image_id}...`);

    // The new image_id came with the presigned post to upload the form data.
    try {
        const pp = obj.presigned_post;
        const formData = new FormData();
        for (const field in pp.fields) {
            formData.append(field, pp.fields[field]);
        }
        formData.append("file", imageFile); // order matters!

        // This uses the AbortController interface.
        // See https://developer.mozilla.org/en-US/docs/Web/API/AbortController
        const ctrl = new AbortController();    // timeout
        setTimeout(() => ctrl.abort(), UPLOAD_TIMEOUT_SECONDS*1000);
        const r = await fetch(pp.url, {
            method: "POST",
            body: formData,
        });
        if (!r.ok) {
            $('#upload_message').html(`Error uploading image status=${r.status} ${r.statusText}`);
            return;
        }
    } catch(e) {
        $('#_message').html(`Timeout (${UPLOAD_TIMEOUT_SECONDS}s) uploading image.`);
        return;
    }
    // Image was uploaded! Clear the form and show the first frame

    $('#message').html('Image uploaded.');
    $('#image-file').val('');   // clear the uploaded image

    enable_disable_upload_button(); // disable the button
    list_uploaded_movies();         // and give us a new list of the uploaded movies
}

/** Run the server's list-upload-movies.
 * This version shows all uploaded movies and requires no authentication.
 */
function list_movies()
{

}


/** The function that is called when the upload_image button is clicked.
 * It validates the image to be uploaded and then calls the upload function.
 */
function upload_image()
{
    const imageFile   = $('#image-file').prop('files')[0];

    if (imageFile.fileSize > MAX_FILE_UPLOAD) {
        $('#message').html(`That file is too big to upload. Please chose a file smaller than ${MAX_FILE_UPLOAD} bytes.`);
        return;
    }
    upload_image_post(imageFile);
}

$( document ).ready( function() {
    console.log("index.html ready function running.")
    // set the correct enable/disable status of the upload button, and configure
    // it to change when any of the form controls change
    enable_disable_upload_button();
    $('.uploadf').on('change', enable_disable_upload_button );
    $('#upload-button').on('click', upload_image);
});