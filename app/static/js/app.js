document.addEventListener("DOMContentLoaded", function () {

    const workspace = document.querySelector(".workspace");

    // =====================================================
    // CRUCE AGENDAMIENTO (v2)
    // =====================================================
    window.showAgendamiento = function () {

        workspace.innerHTML = `
            <h2>Cruce Agendamiento</h2>

            <form id="agendamientoForm">
                <div class="form-group">
                    <label>Archivo Manager</label>
                    <input type="file" name="manager_file" accept=".xls,.xlsx" required>
                </div>

                <div class="form-group">
                    <label>Archivo Bitrix</label>
                    <input type="file" name="bitrix_file" accept=".xls,.xlsx" required>
                </div>

                <button type="submit">Procesar</button>
            </form>
        `;

        const form = document.getElementById("agendamientoForm");

        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            if (!form.manager_file.files.length || !form.bitrix_file.files.length) {
                alert("Debe seleccionar ambos archivos.");
                return;
            }

            const formData = new FormData();
            formData.append("manager_file", form.manager_file.files[0]);
            formData.append("bitrix_file", form.bitrix_file.files[0]);

            try {
                const response = await fetch("/agendamiento-v2/procesar", {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    throw new Error("Error al procesar el agendamiento.");
                }

                const blob = await response.blob();

                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "Agendamiento_v2.xlsx";
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);

            } catch (error) {
                console.error(error);
                alert("Ocurrió un error procesando el agendamiento.");
            }
        });
    };

    // =====================================================
    // INVENTARIO DE CAJAS
    // =====================================================
    window.showInventario = function () {

        workspace.innerHTML = `
            <h2>Inventario de Cajas</h2>

            <form id="inventarioForm">
                <div class="form-group">
                    <label>Archivo de Ventas</label>
                    <input type="file" name="file" accept=".xls,.xlsx" required>
                </div>

                <button type="submit">Procesar</button>
            </form>
        `;

        const form = document.getElementById("inventarioForm");

        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            if (!form.file.files.length) {
                alert("Debe seleccionar un archivo.");
                return;
            }

            const formData = new FormData();
            formData.append("file", form.file.files[0]);

            try {
                const response = await fetch("/inventario/procesar", {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    throw new Error("Error al procesar el inventario.");
                }

                const blob = await response.blob();

                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "Inventario_Cajas.xlsx";
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);

            } catch (error) {
                console.error(error);
                alert("Ocurrió un error procesando el inventario.");
            }
        });
    };

    // =====================================================
    // LIQUIDACION
    // =====================================================
    window.showLiquidacion = function () {

        workspace.innerHTML = `
            <h2>Liquidación</h2>

            <form id="liquidacionForm">
                <div class="form-group">
                    <label>Archivo de Liquidación</label>
                    <input type="file" name="file" accept=".xls,.xlsx" required>
                </div>

                <button type="submit">Generar Recibos</button>
            </form>
        `;

        const form = document.getElementById("liquidacionForm");

        form.addEventListener("submit", async function (e) {
            e.preventDefault();

            if (!form.file.files.length) {
                alert("Debe seleccionar un archivo.");
                return;
            }

            const formData = new FormData();
            formData.append("file", form.file.files[0]);

            try {
                const response = await fetch("/liquidacion/procesar", {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    throw new Error("Error al generar los recibos.");
                }

                const blob = await response.blob();

                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "Recibos_Liquidacion.zip";
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);

            } catch (error) {
                console.error(error);
                alert("Ocurrió un error generando los recibos.");
            }
        });
    };

});
