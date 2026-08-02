"""Batch generation of AI analyses, one per active user.

Each user is processed on its own: a failure is recorded as an `AIAnalysis`
with `status='error'` and the run moves on to the next user.
"""

import time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from ai import services


User = get_user_model()


class Command(BaseCommand):
    help = 'Gera uma análise de IA para cada usuário ativo, usando apenas os dados de cada um.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            dest='email',
            help='Gera a análise apenas para o usuário com este e-mail.',
        )
        parser.add_argument(
            '--skip-empty',
            action='store_true',
            help='Pula os usuários que ainda não têm nenhuma transação.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas lista quem seria processado, sem chamar a API.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if not dry_run and not services.is_enabled():
            raise CommandError(
                'A análise de IA está desligada. Configure DEEPSEEK_API_KEY e '
                'AI_ANALYSIS_ENABLED antes de rodar o comando.'
            )

        users = self.get_users(options['email'], options['skip_empty'])
        if not users:
            self.stdout.write(self.style.WARNING('Nenhum usuário a processar.'))
            return

        if dry_run:
            self.stdout.write(f'{len(users)} usuário(s) seriam processados:')
            for user in users:
                self.stdout.write(f'  - {user.email}')
            return

        self.run_batch(users)

    def get_users(self, email, skip_empty):
        users = User.objects.filter(is_active=True).order_by('email')

        if email:
            users = users.filter(email__iexact=email)
            if not users.exists():
                raise CommandError(f'Nenhum usuário ativo com o e-mail {email}.')

        if skip_empty:
            users = users.filter(transactions__isnull=False).distinct()

        return list(users)

    def run_batch(self, users):
        started_at = time.monotonic()
        successes = 0
        failures = 0

        for user in users:
            self.stdout.write(f'Analisando {user.email}...', ending=' ')

            try:
                analysis = services.run_analysis_for_user(user)
            except Exception as exc:
                # run_analysis_for_user already swallows the agent's own errors;
                # this catches anything left (a database failure, for instance)
                # so one user cannot interrupt the batch.
                failures += 1
                self.stdout.write(self.style.ERROR(f'erro inesperado: {type(exc).__name__}'))
                continue

            if analysis is None:
                failures += 1
                self.stdout.write(self.style.ERROR('a análise de IA está desligada'))
            elif analysis.is_success:
                successes += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'ok (índice {analysis.health_score}, {analysis.duration_ms} ms)'
                    )
                )
            else:
                failures += 1
                self.stdout.write(self.style.ERROR(analysis.error_message))

        self.write_summary(len(users), successes, failures, time.monotonic() - started_at)

    def write_summary(self, total, successes, failures, elapsed_seconds):
        style = self.style.SUCCESS if not failures else self.style.WARNING
        self.stdout.write('')
        self.stdout.write(style(f'{total} usuário(s) processados em {elapsed_seconds:.1f}s'))
        self.stdout.write(self.style.SUCCESS(f'  sucessos: {successes}'))
        self.stdout.write(
            self.style.ERROR(f'  falhas: {failures}')
            if failures
            else f'  falhas: {failures}'
        )
