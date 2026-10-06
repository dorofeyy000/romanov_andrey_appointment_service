async function request(url,options={}){
    const response=await fetch(url,{credentials:"include",...options});
    const data=await response.json();
    if(!response.ok) throw new Error(data.detail||"Ошибка");
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
        document.getElementById("loginStatus").textContent="";
        await load();
    }catch(error){
        document.getElementById("loginStatus").textContent=error.message;
    }
}

async function logout(){
    await request("/api/auth/logout",{method:"POST"});
    document.getElementById("content").classList.add("hidden");
    document.getElementById("login").classList.remove("hidden");
}

async function load(){
    try{
        const slots=await request("/api/slots?available=true&limit=20");
        document.getElementById("slots").innerHTML=slots.map(s=>
            `<button onclick="book(${s.specialist_id},${s.service_id},${s.id})">
            Слот #${s.id}: ${new Date(s.start_at).toLocaleString()}
            </button>`
        ).join("");

        const appointments=await request("/api/appointments?page=1&size=20");
        document.getElementById("appointments").innerHTML=appointments.items.length
            ? appointments.items.map(a=>
                `<div>
                Запись #${a.id} — ${a.status}
                ${a.status==="booked"?`<button onclick="cancelAppointment(${a.id})">Отменить</button>`:""}
                </div>`
            ).join("")
            : "Записей пока нет";

        const summary=await request("/api/summary");
        document.getElementById("summary").textContent=JSON.stringify(summary,null,2);
    }catch(error){
        alert(error.message);
    }
}

async function book(specialist_id,service_id,slot_id){
    try{
        await request("/api/appointments",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({specialist_id,service_id,slot_id})
        });
        await load();
    }catch(error){
        alert(error.message);
    }
}

async function cancelAppointment(id){
    try{
        await request(`/api/appointments/${id}/cancel`,{method:"POST"});
        await load();
    }catch(error){
        alert(error.message);
    }
}