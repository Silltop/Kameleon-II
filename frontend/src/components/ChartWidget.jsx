import { useRef, useEffect } from 'preact/hooks'
import Chart from 'chart.js/auto'

export function ChartWidget({ id, type = 'pie', data = [], precision = 0, title = '' }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    if (!canvasRef.current) return
    const ctx = canvasRef.current.getContext('2d')

    const labels = data.map(d => d.label)
    const values = data.map(d => (typeof d.value === 'number' ? d.value : parseFloat(d.value)))
    const colors = data.map(d => d.color || 'rgba(54, 162, 235, 0.2)')

    const chart = new Chart(ctx, {
      type: type,
      data: {
        labels,
        datasets: [{ data: values, backgroundColor: colors }],
      },
      options: {
        responsive: false,
        plugins: {
          title: { display: !!title, text: title },
          legend: { display: false },
        },
        scales: {
          y: {
            ticks: {
              precision: precision,
            },
          },
        },
      },
    })

    return () => {
      chart.destroy()
    }
  }, [id, type, precision, title, JSON.stringify(data)])

  return (
    <div className="flex-shrink-0 p-6">
      <canvas id={id} ref={canvasRef} width="250" height="150"></canvas>
    </div>
  )
}
