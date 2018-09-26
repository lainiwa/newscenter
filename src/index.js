import Vue from 'vue';
import axios from 'axios';
import io from 'socket.io-client';

var app = new Vue({
    el: '#app',
    data: {
        message: 'Привет, Vue!',
        files: {
            data: new FormData(),
            total: 0,
            celeryResult: [],
        },
        socket: io.connect('http://localhost:9998/test'),
    },
    methods: {
        fileChange(fileList) {
            let file;
            for (file of fileList) {
                this.files.total++
                this.files.data.append('file[]', file, file.name);
            }
            // console.log(JSON.stringify(this.files.data))
        },
        upload() {
            // console.log(JSON.stringify(this.files.data))
            document.getElementById('fileUploadForm').reset();
            axios({ method: 'POST', 'url': '/upload', 'data': this.files.data }).then(result => {
                // console.dir(result.data);
            }, error => {
                console.error(error);
            });
            // e.preventDefault();
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
            self.socket.on('confirmation', function(message){
                console.log(message.connection_confirmation)
            });
        })
    }
})