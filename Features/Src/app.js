const express = require('express');
const authRoutes = require('./routes/authRoutes');
const app = express();

app.use(express.json()); // Necesario para recibir JSON
app.use('/api/auth', authRoutes);

app.listen(3000, () => console.log('Servidor en puerto 3000'));
