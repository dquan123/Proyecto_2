// ==============================
// NODOS
// ==============================

// Usuarios
CREATE (:Usuario {id: 'U1', nombre: 'Andrea López', edad: 20});
CREATE (:Usuario {id: 'U2', nombre: 'Luis Torres', edad: 24});

// Preferencias
CREATE (:Preferencia {nombre: 'buena cámara'});
CREATE (:Preferencia {nombre: 'buena batería'});
CREATE (:Preferencia {nombre: 'pantalla grande'});

// Características técnicas
CREATE (:Caracteristica {nombre: 'Cámara', valor: '50MP'});
CREATE (:Caracteristica {nombre: 'Batería', valor: '5000mAh'});
CREATE (:Caracteristica {nombre: 'Pantalla', valor: '6.7 pulgadas'});

// Teléfonos
CREATE (:Telefono {nombre: 'Samsung Galaxy A54', marca: 'Samsung', precio: 4500});
CREATE (:Telefono {nombre: 'iPhone 13 Pro', marca: 'Apple', precio: 9500});

// Marcas
CREATE (:Marca {nombre: 'Samsung'});
CREATE (:Marca {nombre: 'Apple'});

// Rangos de precios
CREATE (:RangoPrecio {min: 4000, max: 5000});
CREATE (:RangoPrecio {min: 9000, max: 10000});


// ==============================
// RELACIONES
// ==============================

// Usuario → Preferencia
MATCH (u:Usuario {id: 'U1'}), (p:Preferencia {nombre: 'buena cámara'}) CREATE (u)-[:PREFIERE]->(p);
MATCH (u:Usuario {id: 'U1'}), (p:Preferencia {nombre: 'buena batería'}) CREATE (u)-[:PREFIERE]->(p);
MATCH (u:Usuario {id: 'U2'}), (p:Preferencia {nombre: 'pantalla grande'}) CREATE (u)-[:PREFIERE]->(p);
MATCH (u:Usuario {id: 'U2'}), (p:Preferencia {nombre: 'buena cámara'}) CREATE (u)-[:PREFIERE]->(p);

// Preferencia → Característica
MATCH (p:Preferencia {nombre: 'buena cámara'}), (c:Caracteristica {nombre: 'Cámara'}) CREATE (p)-[:BUSCA]->(c);
MATCH (p:Preferencia {nombre: 'buena batería'}), (c:Caracteristica {nombre: 'Batería'}) CREATE (p)-[:BUSCA]->(c);
MATCH (p:Preferencia {nombre: 'pantalla grande'}), (c:Caracteristica {nombre: 'Pantalla'}) CREATE (p)-[:BUSCA]->(c);

// Teléfono → Característica
MATCH (t:Telefono {nombre: 'Samsung Galaxy A54'}), 
      (c1:Caracteristica {nombre: 'Cámara'}),
      (c2:Caracteristica {nombre: 'Batería'}),
      (c3:Caracteristica {nombre: 'Pantalla'})
CREATE (t)-[:TIENE]->(c1), (t)-[:TIENE]->(c2), (t)-[:TIENE]->(c3);

MATCH (t:Telefono {nombre: 'iPhone 13 Pro'}), 
      (c1:Caracteristica {nombre: 'Cámara'}),
      (c2:Caracteristica {nombre: 'Batería'}),
      (c3:Caracteristica {nombre: 'Pantalla'})
CREATE (t)-[:TIENE]->(c1), (t)-[:TIENE]->(c2), (t)-[:TIENE]->(c3);

// Teléfono → Marca
MATCH (t:Telefono {nombre: 'Samsung Galaxy A54'}), (m:Marca {nombre: 'Samsung'}) CREATE (t)-[:ES_DE_LA_MARCA]->(m);
MATCH (t:Telefono {nombre: 'iPhone 13 Pro'}), (m:Marca {nombre: 'Apple'}) CREATE (t)-[:ES_DE_LA_MARCA]->(m);

// Teléfono → RangoPrecio
MATCH (t:Telefono {nombre: 'Samsung Galaxy A54'}), (r:RangoPrecio {min: 4000}) CREATE (t)-[:PERTENECE_A]->(r);
MATCH (t:Telefono {nombre: 'iPhone 13 Pro'}), (r:RangoPrecio {min: 9000}) CREATE (t)-[:PERTENECE_A]->(r);

// Usuario → Teléfono (Calificación)
MATCH (u:Usuario {id: 'U1'}), (t:Telefono {nombre: 'Samsung Galaxy A54'}) CREATE (u)-[:CALIFICO {estrellas: 4}]->(t);
MATCH (u:Usuario {id: 'U2'}), (t:Telefono {nombre: 'iPhone 13 Pro'}) CREATE (u)-[:CALIFICO {estrellas: 5}]->(t);
