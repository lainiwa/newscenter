import Vue from 'vue';
import axios from 'axios';
import io from 'socket.io-client';

var app = new Vue({
    el: '#app',

    data() {
        // Initial upload files related information
        let filesInitVal = () => ({
            reset: filesInitVal,
            data: new FormData(),
            total: 0,
            celeryResult: [],
        });
        // Data
        return {
            message: 'Привет, Vue!',
            files: filesInitVal(),
            socket: io.connect('http://localhost:9998/test'),
        };
    },

    methods: {
        fileChange(fileList) {
            let file;
            for (file of fileList) {
                this.files.total++;
                this.files.data.append('file[]', file, file.name);
            };
            // console.log(JSON.stringify(this.files.data))
        },
        upload() {
            // Clear form
            document.getElementById('fileUploadForm').reset();
            // Upload images to server
            axios({ method: 'POST', url: '/upload', data: this.files.data }).then(result => {
                // console.dir(result.data);
            }, error => {
                console.error(error);
            });
            // Clear form related data
            this.files = this.files.reset();
        },
        deleteFile(filename) {
            // Message for this particular file
            let message = this.files.celeryResult.filter(x => x['image'] == filename)[0]
            // If file conversion was successfull (i.e. file exists on server)
            if (message.success) {
                // Delete image from server
                axios({ method: 'POST', url: '/delete_image', data: { filename: filename } }).then(result => {
                    // console.dir(result.data);
                }, error => {
                    console.error(error);
                });
            }
            // Remove file from `this.files`
            this.files.total--;
            this.files.celeryResult = this.files.celeryResult.filter(x => x['image'] != filename);
        },
    },

    mounted: function() {
        let self = this
        this.$nextTick(function() {
            // Код, который будет запущен только после
            // отображения всех представлений
            self.socket.on('connect', function() {
                self.socket.emit('connection', { connection_confirmation: 'you are connected to the socket!' });
            });

            // 'confirmation' event received by the client invokes the callback function which confirms the socket connection
            self.socket.on('confirmation', function(message) {
                console.log(message.image, message.success)
                self.files.celeryResult.push(message);
            });
        })
    },

})
