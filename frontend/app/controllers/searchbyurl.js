import Ember from 'ember';

export default Ember.Controller.extend({

  actions: {
    addByUrl() {
      console.log("addByUrl" );

      let url = this.get('foobar');
      console.log("addByUrl", url );
 
    },

    findByUrl() {
      console.log("findByUrl");
      let url = this.get('foobar');
      console.log("findByUrl", url);
    }
  }
});
