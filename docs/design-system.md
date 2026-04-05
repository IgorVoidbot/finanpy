# Design System

Interface em tema escuro, estilizada com TailwindCSS via CDN.

## Paleta de Cores

| Papel | Classe Tailwind | Uso |
|---|---|---|
| Background principal | `bg-gray-950` | Fundo do body |
| Background cards | `bg-gray-900` | Cards, sidebar, modals |
| Background inputs | `bg-gray-800` | Campos de formulário |
| Border padrão | `border-gray-700` | Bordas de cards, inputs, dividers |
| Texto primário | `text-gray-100` | Títulos, texto principal |
| Texto secundário | `text-gray-400` | Labels, descrições, placeholders |
| Accent primário | `bg-emerald-500` | Botões primários, entradas |
| Accent hover | `hover:bg-emerald-600` | Hover de botões primários |
| Accent secundário | `bg-violet-500` | Badges, links ativos |
| Perigo | `bg-rose-500` | Botão excluir, valores de saída |
| Sucesso | `text-emerald-400` | Valores de entrada, saldo positivo |
| Alerta | `text-amber-400` | Avisos |
| Gradient header | `bg-gradient-to-r from-emerald-500 to-violet-500` | Logo, títulos especiais |

## Tipografia

| Elemento | Classes Tailwind |
|---|---|
| Título da página (h1) | `text-2xl font-bold text-gray-100` |
| Subtítulo (h2) | `text-xl font-semibold text-gray-100` |
| Título de card (h3) | `text-lg font-semibold text-gray-100` |
| Corpo de texto | `text-sm text-gray-300` |
| Label | `text-sm font-medium text-gray-400` |
| Texto auxiliar | `text-xs text-gray-500` |

## Botões

```html
<!-- Primário -->
<button class="bg-emerald-500 hover:bg-emerald-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200">
    Salvar
</button>

<!-- Secundário -->
<button class="bg-gray-700 hover:bg-gray-600 text-gray-200 font-medium py-2 px-4 rounded-lg transition-colors duration-200">
    Cancelar
</button>

<!-- Perigo -->
<button class="bg-rose-500 hover:bg-rose-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200">
    Excluir
</button>

<!-- Outline -->
<button class="border border-gray-600 hover:border-emerald-500 text-gray-300 hover:text-emerald-400 font-medium py-2 px-4 rounded-lg transition-colors duration-200">
    Ver detalhes
</button>
```

## Inputs e Formulários

```html
<!-- Campo de texto -->
<div class="mb-4">
    <label class="block text-sm font-medium text-gray-400 mb-1">E-mail</label>
    <input type="email"
        class="w-full bg-gray-800 border border-gray-700 rounded-lg py-2 px-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors duration-200"
        placeholder="seu@email.com">
</div>

<!-- Select -->
<select class="w-full bg-gray-800 border border-gray-700 rounded-lg py-2 px-3 text-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors duration-200">
    <option value="">Selecione...</option>
</select>

<!-- Form container -->
<form class="bg-gray-900 border border-gray-700 rounded-xl p-6 space-y-4">
    <!-- campos -->
</form>
```

## Cards

```html
<!-- Card padrão -->
<div class="bg-gray-900 border border-gray-700 rounded-xl p-6">
    <h3 class="text-lg font-semibold text-gray-100 mb-2">Título</h3>
    <p class="text-sm text-gray-400">Conteúdo</p>
</div>

<!-- Card com destaque (dashboard) -->
<div class="bg-gray-900 border border-gray-700 rounded-xl p-6 border-t-2 border-t-emerald-500">
    <h3 class="text-lg font-semibold text-gray-100 mb-2">Saldo Total</h3>
    <p class="text-3xl font-bold text-emerald-400">R$ 5.230,00</p>
</div>
```

## Layout

```html
<!-- Container principal (usuário logado) -->
<div class="min-h-screen bg-gray-950 text-gray-100">
    <nav class="bg-gray-900 border-b border-gray-700 px-6 py-3"><!-- navbar --></nav>
    <div class="flex">
        <aside class="hidden md:block w-64 bg-gray-900 border-r border-gray-700 min-h-screen p-4">
            <!-- sidebar -->
        </aside>
        <main class="flex-1 p-6"><!-- conteúdo --></main>
    </div>
</div>

<!-- Grid responsivo (dashboard) -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <!-- cards -->
</div>

<!-- Tabela responsiva -->
<div class="overflow-x-auto">
    <table class="w-full text-sm text-left">
        <thead class="text-xs text-gray-400 uppercase bg-gray-800">
            <tr><th class="px-4 py-3">Coluna</th></tr>
        </thead>
        <tbody class="divide-y divide-gray-700">
            <tr class="bg-gray-900 hover:bg-gray-800 transition-colors">
                <td class="px-4 py-3 text-gray-300">Valor</td>
            </tr>
        </tbody>
    </table>
</div>
```

## Navbar e Sidebar

```html
<!-- Navbar -->
<nav class="bg-gray-900/80 backdrop-blur-sm border-b border-gray-700 px-6 py-3 flex items-center justify-between sticky top-0 z-50">
    <a href="/" class="text-xl font-bold bg-gradient-to-r from-emerald-400 to-violet-400 bg-clip-text text-transparent">
        Finanpy
    </a>
    <div class="flex items-center gap-4">
        <span class="text-sm text-gray-400">Olá, {{ user.first_name }}</span>
        <a href="{% url 'logout' %}" class="text-sm text-gray-400 hover:text-rose-400 transition-colors">Sair</a>
    </div>
</nav>

<!-- Item de sidebar -->
<a href="#" class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-800 transition-colors duration-200">
    <span class="text-sm font-medium">Dashboard</span>
</a>

<!-- Item de sidebar ativo -->
<a href="#" class="flex items-center gap-3 px-3 py-2 rounded-lg text-emerald-400 bg-emerald-500/10">
    <span class="text-sm font-medium">Dashboard</span>
</a>
```

## Mensagens de Feedback (Django Messages)

```html
<!-- Sucesso -->
<div class="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg px-4 py-3 text-sm">
    Operação realizada com sucesso!
</div>

<!-- Erro -->
<div class="bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-lg px-4 py-3 text-sm">
    Erro ao processar sua solicitação.
</div>

<!-- Alerta -->
<div class="bg-amber-500/10 border border-amber-500/30 text-amber-400 rounded-lg px-4 py-3 text-sm">
    Atenção: verifique os campos destacados.
</div>
```

## Modal de Confirmação

```html
<div class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
    <div class="bg-gray-900 border border-gray-700 rounded-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold text-gray-100 mb-2">Confirmar exclusão</h3>
        <p class="text-sm text-gray-400 mb-6">Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.</p>
        <div class="flex justify-end gap-3">
            <button class="bg-gray-700 hover:bg-gray-600 text-gray-200 font-medium py-2 px-4 rounded-lg">Cancelar</button>
            <button class="bg-rose-500 hover:bg-rose-600 text-white font-medium py-2 px-4 rounded-lg">Excluir</button>
        </div>
    </div>
</div>
```
