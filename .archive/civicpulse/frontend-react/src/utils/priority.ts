export function priorityScore(severity: number, recurrence: number, pendingTime: number, publicImpact: number): number {
  const values = [severity,recurrence,pendingTime,publicImpact].map(value => Number.isFinite(value) ? Math.min(100,Math.max(0,value)) : 0);
  return Math.round(values[0]*0.4 + values[1]*0.25 + values[2]*0.2 + values[3]*0.15);
}
