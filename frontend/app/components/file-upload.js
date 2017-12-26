import Ember from 'ember';

import EmberUploader from 'ember-uploader';

export default EmberUploader.FileField.extend({
  value: 'default',
  set_upload_results: null,
  update_progress_bar: null,

  init() {
    this._super(...arguments);
  },

  filesDidChange: function(files) {
    const uploader = EmberUploader.Uploader.create({
      url: this.get('url')
    });

    if (!Ember.isEmpty(files)) {
      // this second argument is optional and can to be sent as extra data with the upload
      let res = uploader.upload(files[0], { "whatever": "something" });
//      console.log("upload result", res);
    }

    uploader.on('progress', e => {
      let update_progress_bar = this.get('update_progress_bar');
      let set_upload_results = this.get('set_upload_results');
      update_progress_bar(e.percent)
      set_upload_results({})
//      console.log("progress -> " + e.percent);

    });

    uploader.on('didUpload', response => {
      let set_upload_results = this.get('set_upload_results');
//      console.log("didUpload -> ",  response['data']);

      set_upload_results(response);
    });

    uploader.on('didError', (jqXHR, textStatus, errorThrown) => {
      let set_upload_results = this.get('set_upload_results');
//      console.log("didError -> ",  jqXHR);
//      console.log("statusText            -> ",  jqXHR.statusText);
//      console.log("didError errorThrown  -> ",  jqXHR.errorThrown);
//      console.log("didError responseText -> ",  jqXHR.responseText);

      let message = jqXHR.responseText;

      set_upload_results({
        'success': false,
        'error': message,
        'result': jqXHR.statusText
      });

    });
  }
});
