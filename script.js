const canvas = document.getElementById('webgl-canvas');
const gl = canvas.getContext('webgl');

const vertexShaderSource = `
    attribute vec4 position;
    uniform mat4 modelViewMatrix;
    uniform mat4 projectionMatrix;
    void main() {
        gl_Position = projectionMatrix * modelViewMatrix * position;
    }
`;

const fragmentShaderSource = `
    precision mediump float;
    void main() {
        gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
`;

const vertexShader = gl.createShader(gl.VERTEX_SHADER);
gl.shaderSource(vertexShader, vertexShaderSource);
gl.compileShader(vertexShader);

const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
gl.shaderSource(fragmentShader, fragmentShaderSource);
gl.compileShader(fragmentShader);

const shaderProgram = gl.createProgram();
gl.attachShader(shaderProgram, vertexShader);
gl.attachShader(shaderProgram, fragmentShader);
gl.linkProgram(shaderProgram);
gl.useProgram(shaderProgram);

const positionAttributeLocation = gl.getAttribLocation(shaderProgram, 'position');
const modelViewMatrixUniformLocation = gl.getUniformLocation(shaderProgram, 'modelViewMatrix');
const projectionMatrixUniformLocation = gl.getUniformLocation(shaderProgram, 'projectionMatrix');

const items = [];  // Array to store item data retrieved from the API

function drawScene() {
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

    const projectionMatrix = mat4.create();
    mat4.perspective(projectionMatrix, Math.PI / 4, canvas.clientWidth / canvas.clientHeight, 0.1, 100);

    const modelViewMatrix = mat4.create();
    mat4.translate(modelViewMatrix, modelViewMatrix, [-1.5, 0, -7]);

    gl.uniformMatrix4fv(modelViewMatrixUniformLocation, false, modelViewMatrix);
    gl.uniformMatrix4fv(projectionMatrixUniformLocation, false, projectionMatrix);

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);

    // Create cube geometry
    const vertices = new Float32Array([
        -1, -1, -1,
        1, -1, -1,
        1, 1, -1,
        -1, 1, -1,
        -1, -1, 1,
        1, -1, 1,
        1, 1, 1,
        -1, 1, 1,
    ]);

    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(positionAttributeLocation);
    gl.vertexAttribPointer(positionAttributeLocation, 3, gl.FLOAT, false, 0, 0);

    // Draw each cube for items
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        const translationMatrix = mat4.create();
        mat4.translate(translationMatrix, translationMatrix, [i * 3, 0, 0]);  // Position each cube horizontally
        gl.uniformMatrix4fv(modelViewMatrixUniformLocation, false, translationMatrix);
        gl.drawArrays(gl.TRIANGLE_FAN, 0, 4);
        gl.drawArrays(gl.TRIANGLE_FAN, 4, 4);
        gl.drawArrays(gl.LINE_LOOP, 0, 4);
        gl.drawArrays(gl.LINE_LOOP, 4, 4);
    }
}

// Fetch data from the API and update the items array
async function fetchData() {
    const response = await fetch('/items');
    const data = await response.json();
    items.push(...data.items);
    drawScene();
}

fetchData();
