let currentPage=1;

async function request(url,options={}){
    const response=await fetch(url,{credentials:"include",...options});
    const data=await response.json();

    if(!response.ok){
        throw new Error(data.detail||"Ошибка");
    }

    return data;
}

async function login(){
    try{
        await request("/api/auth/login",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                username:document.getElementById("username").value,
                password:document.getElementById("password").value
            })
        });

        document.getElementById("login").classList.add("hidden");
        document.getElementById("content").classList.remove("hidden");

        await loadAppointments(1);
    }catch(error){
        document.getElementById("loginStatus").textContent=error.message;
    }
}

async function logout(){
    await request("/api/auth/logout",{method:"POST"});
    document.getElementById("content").classList.add("hidden");
    document.getElementById("login").classList.remove("hidden");
}

function showScreen(id){
    document.querySelectorAll(".screen").forEach(screen=>{
        screen.classList.add("hidden");
    });

    document.getElementById(id).classList.remove("hidden");

    if(id==="summaryScreen"){
        loadSummary();
    }

    if(id==="listScreen"){
        loadAppointments(currentPage);
    }
}

async function loadAppointments(page=1){
    currentPage=page;

    try{
        const status=document.getElementById("statusFilter").value;
        const size=document.getElementById("pageSize").value;

        let url=`/api/appointments?page=${page}&size=${size}`;

        if(status){
            url+=`&status=${encodeURIComponent(status)}`;
        }

        const data=await request(url);

        document.getElementById("appointments").innerHTML=data.items.length
            ? data.items.map(item=>`
                <div class="appointment">
                    <div>
                        <strong>Запись #${item.id}</strong>
                    </div>
                    <div>Специалист: ${item.specialist_name}</div>
                    <div>Услуга: ${item.service_name}</div>
                    <div>Начало: ${new Date(item.slot_start).toLocaleString()}</div>
                    <div>Статус: ${item.status}</div>
                    <button onclick="openCard(${item.id})">Карточка</button>
                    ${item.status==="booked"
                        ?`<button onclick="cancelAppointment(${item.id})">Отменить</button>`
                        :""
                    }
                </div>
            `).join("")
            : "Записей нет";

        const sizeNumber=Number(size);
        const pages=Math.max(1,Math.ceil(data.total/sizeNumber));

        let pagination="";

        if(page>1){
            pagination+=`<button onclick="loadAppointments(${page-1})">Назад</button>`;
        }

        pagination+=` Страница ${page} из ${pages} `;

        if(page<pages){
            pagination+=`<button onclick="loadAppointments(${page+1})">Вперёд</button>`;
        }

        document.getElementById("pagination").innerHTML=pagination;
    }catch(error){
        alert(error.message);
    }
}

function openCard(id){
    document.getElementById("appointmentId").value=id;
    showScreen("cardScreen");
    loadAppointmentCard();
}

async function loadAppointmentCard(){
    const id=document.getElementById("appointmentId").value;

    if(!id){
        return;
    }

    try{
        const item=await request(`/api/appointments/${id}`);

        document.getElementById("appointmentCard").innerHTML=`
            <div class="card">
                <h3>Запись #${item.id}</h3>
                <p>Специалист: ${item.specialist_name}</p>
                <p>Специальность ID: ${item.specialist_id}</p>
                <p>Услуга: ${item.service_name}</p>
                <p>ID услуги: ${item.service_id}</p>
                <p>Слот: ${item.slot_id}</p>
                <p>Начало: ${new Date(item.slot_start).toLocaleString()}</p>
                <p>Окончание: ${new Date(item.slot_end).toLocaleString()}</p>
                <p>Статус: ${item.status}</p>
                <p>Создана: ${new Date(item.created_at).toLocaleString()}</p>
            </div>
        `;
    }catch(error){
        document.getElementById("appointmentCard").textContent=error.message;
    }
}

async function cancelAppointment(id){
    try{
        await request(`/api/appointments/${id}/cancel`,{
            method:"POST"
        });

        await loadAppointments(currentPage);
    }catch(error){
        alert(error.message);
    }
}

async function loadSummary(){
    try{
        const summary=await request("/api/summary");
        document.getElementById("summary").textContent=
            JSON.stringify(summary,null,2);
    }catch(error){
        document.getElementById("summary").textContent=error.message;
    }
}