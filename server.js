const express = require('express');
const bodyParser = require('body-parser');
const http = require('http');
const socketIO = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
    cors: {
        origin: '*',
    }
});

app.use(bodyParser.json());

let orders = [];

// Route to handle incoming orders
app.post('/add-order', (req, res) => {
    const newOrder = req.body.items;
    orders.push(newOrder);
    console.log('Received new order:', newOrder);

    // Send the new order to all connected clients via Socket.IO
    io.emit('newOrder', newOrder);

    res.status(200).json({ message: 'Order received successfully.' });
});

// Route to serve the HTML page
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

io.on('connection', (socket) => {
    // Send all existing orders to the newly connected client
    socket.emit('initialOrders', orders);
});

server.listen(3000, () => {
    console.log('Server is running on port 3000');
});
