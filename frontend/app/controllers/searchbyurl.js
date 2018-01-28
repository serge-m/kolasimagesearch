import Ember from 'ember';

export default Ember.Controller.extend({
  ajax: Ember.inject.service(),

  actions: {
    addByUrl() {
      const ajax = this.get('ajax');
      console.log("addByUrl" );

      let url = this.get('image_url');
      console.log("addByUrl", url );
      
      ajax.request('/add_by_url',  {
        method: 'POST',
        data: {
          url: url
        }
      }).then(response => {this.set('upload_res', response);});

    },

    findByUrl() {
      const ajax = this.get('ajax');
     

      //console.log("findByUrl");
      let url = this.get('image_url');
      //console.log("findByUrl", url);

      ajax.request('/find_by_url',  {
        method: 'POST',
        data: {
          url: url
        }
      }).then(response => {this.set('upload_res', response);});
    }
  }
});
