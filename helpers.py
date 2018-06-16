import os
import subprocess

from app import app
import db


COVERS_DIR = os.path.join(app.static_folder, 'covers')
PDFS_DIR = os.path.join(app.static_folder, 'pdfs')


def init_db():
    with app.app_context():
        schema_file = os.path.join(app.root_path, 'db.schema')
        schema = open(schema_file, 'r')

        cur = db.get().cursor()
        cur.executescript(schema.read())

        schema.close()
        cur.close()

        db.get().commit()


def generate_db_issues_from_pdfs(year, month, day):
    with app.app_context():
        for pdf in os.listdir(PDFS_DIR):
            number = pdf.split('.')[0]
            date = '{}-{:02}-{:02}'.format(year, month, day)
            db.query(
                'INSERT INTO issues (number, date) VALUES (?, ?)',
                (number, date)
            )

            if day == 15 and month == 12:
                year += 1

            if month == 1 or month == 8:
                day = 1
                month += 1
            else:
                if day == 15:
                    if month == 12:
                        month = 1
                    else:
                        month += 1

                if day == 1:
                    day = 15
                else:
                    day = 1

        db.get().commit()


def generate_translations():
    messages_pot_file_path = os.path.join(app.root_path, 'messages.pot')
    translations_dir_path = os.path.join(app.root_path, 'translations')
    sr_latn_rs_po_file_path = os.path.join(
        messages_pot_file_path,
        'sr_Latn_RS/LC_MESSAGES/messages.po'
    )

    subprocess.run([
        'pybabel', 'extract',
        '-F', 'babel.cfg',
        '-o', messages_pot_file_path,
        app.root_path
    ])

    subprocess.run([
        'pybabel', 'init',
        '-l', 'sr_Latn_RS',
        '-d', translations_dir_path,
        '-i', messages_pot_file_path
    ])

    subprocess.run([
        'msgen',
        '-i', messages_pot_file_path,
        '-o', sr_latn_rs_po_file_path
    ])

    with open(sr_latn_rs_po_file_path, 'r') as sr_latn_rs_po_file:
        subprocess.run([
            'msgfilter',
            '-o', sr_latn_rs_po_file_path,
            'recode-sr-latin'
        ], stdin=sr_latn_rs_po_file)

    subprocess.run([
        'pybabel', 'compile', '-f',
        '-d', translations_dir_path
    ])


def generate_covers():
    os.mkdir(COVERS_DIR)

    pdfs_paths = os.listdir(PDFS_DIR)
    for i, pdf_path in enumerate(pdfs_paths, start=1):
        print('[{:>{}}/{}] Generating covers for {}...'.format(
            i, len(str(len(pdfs_paths))), len(pdfs_paths), pdf_path
        ))

        large_cover_path = '{}-large.png'.format(
            os.path.join(COVERS_DIR, pdf_path.split('.')[0])
        )

        subprocess.run([
            'convert',
            '-density', '200',
            '{}[0]'.format(os.path.join(PDFS_DIR, pdf_path)),
            '-background', 'white',
            '-flatten',
            '-alpha', 'off',
            '-resize', 'x1200',
            'png24:{}'.format(large_cover_path)
        ])

        subprocess.run([
            'convert',
            '-density', '200',
            large_cover_path,
            '-background', 'white',
            '-flatten',
            '-alpha', 'off',
            '-resize', '250x',
            'png24:{}-small.png'.format(
                os.path.join(COVERS_DIR, pdf_path.split('.')[0])
            )
        ])
