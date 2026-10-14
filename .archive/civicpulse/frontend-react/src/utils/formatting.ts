export const formatDate = (value: string) => new Intl.DateTimeFormat('en-IN',{day:'numeric',month:'short',year:'numeric'}).format(new Date(value));
export const formatDateTime = (value: string) => new Intl.DateTimeFormat('en-IN',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(value));
