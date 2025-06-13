import { useEffect, useState } from 'react'

export default function Bills() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXJfMTIzIiwibmFtZSI6IlRlc3QgVXNlciIsImVtYWlsIjoidGVzdEBleGFtcGxlLmNvbSIsImlhdCI6MTc0OTY1ODE2MCwiZXhwIjoxNzQ5NzQ0NTYwfQ.PeRF-It1XbHpDSt7KMKRgyNbMt8gZWwZymzbPBvNu7I"

  useEffect(() => {
    const payload = {
      account_number: "1234567890",
      period: "2024-05"
    }

    fetch('http://127.0.0.1:8003/api/v1/bills?account_number=8&period=2024-05', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json' ,
        'Authorization': `Bearer ${token}`
      },
      
    })
      .then(res => res.json())
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Загрузка...</p>
  console.log(data)
  if (!data) return <p>Ошибка загрузки данных</p>
  

  return (
    <div className="bills">
      <h2>Счет за период: {data.period}</h2>
      <p><strong>Лицевой счет:</strong> {data.account_number}</p>
      <p><strong>Статус:</strong> {data.status}</p>
      <p><strong>Сумма к оплате:</strong> {data.total_amount} ₽</p>

      <h3>Услуги</h3>
      <ul>
        {data.services.map((s, index) => (
          <li key={index}>
            <p><strong>{s.service_name}</strong></p>
            <p>Цена за единицу: {s.cost_per_unit}</p>
            <p>Количество: {s.units}</p>
            <p>Итого: {s.total_cost}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}
